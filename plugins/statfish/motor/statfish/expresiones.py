"""Expresiones del modelo: un subconjunto seguro de Python, validado sobre `ast`.

Se acepta solo esto (referencias/expresiones.md):

- nombres de atributos del usuario, argumentos del estado y locales;
- `p.<parámetro>` y `d.<distribución>.<valor>`;
- números, textos y True/False;
- comparaciones, `in` y `not in`;
- `and`, `or` y `not`;
- `+`, `-`, `*` y `/`;
- `x if c else y`;
- `min` y `max`;
- tuplas y listas literales (para `in`).

Cualquier otra cosa es un error de validación. Una expresión válida se traduce a código Python que
solo indexa diccionarios conocidos (`u`, `P`, `D`) o variables locales con prefijo; por eso se puede
compilar sin abrir nada más que `min` y `max`.
"""
import ast
import copy
import re

_NODOS = (
    ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not, ast.USub, ast.UAdd,
    ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Compare, ast.Eq, ast.NotEq, ast.Lt,
    ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn, ast.IfExp, ast.Constant, ast.Name, ast.Load,
    ast.Attribute, ast.Call, ast.Tuple, ast.List,
)
FUNCIONES = ('min', 'max')
RESERVADOS = ('p', 'd', 'min', 'max', 'True', 'False', 'None')
_ID = re.compile(r'^[A-Za-z][A-Za-z0-9_]*$')


class ErrorExpresion(ValueError):
    """Una expresión del modelo que no cumple la gramática permitida."""


class Analisis:
    """Resultado de validar una expresión: el árbol y los nombres que usa."""

    __slots__ = ('texto', 'arbol', 'nombres', 'parametros', 'distribuciones')

    def __init__(self, texto, arbol, nombres, parametros, distribuciones):
        self.texto = texto
        self.arbol = arbol
        self.nombres = nombres
        self.parametros = parametros
        self.distribuciones = distribuciones


def analizar(texto):
    """Valida `texto` y devuelve su `Analisis`. Lanza ErrorExpresion si no cumple."""
    if isinstance(texto, bool):
        texto = 'True' if texto else 'False'
    elif isinstance(texto, (int, float)):
        texto = repr(texto)
    if not isinstance(texto, str) or not texto.strip():
        raise ErrorExpresion(f'expresión vacía o de tipo no válido: {texto!r}')
    try:
        arbol = ast.parse(texto.strip(), mode='eval')
    except SyntaxError as e:
        raise ErrorExpresion(f'sintaxis no válida en «{texto}»: {e.msg}') from None
    nombres, parametros, distribuciones = set(), set(), set()
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, _NODOS):
            raise ErrorExpresion(f'«{texto}» usa {type(nodo).__name__}, que no está permitido')
        if isinstance(nodo, ast.Constant):
            if not isinstance(nodo.value, (bool, int, float, str)):
                raise ErrorExpresion(f'«{texto}» usa la constante {nodo.value!r}, que no está permitida')
        elif isinstance(nodo, ast.Call):
            if not (isinstance(nodo.func, ast.Name) and nodo.func.id in FUNCIONES):
                raise ErrorExpresion(f'«{texto}» llama a una función no permitida (solo min y max)')
            if nodo.keywords or len(nodo.args) < 2:
                raise ErrorExpresion(f'«{texto}»: min y max llevan dos o más argumentos, sin nombres')
        elif isinstance(nodo, ast.Attribute):
            _validar_atributo(nodo, texto, parametros, distribuciones)
        elif isinstance(nodo, ast.Name):
            pass
    # Los nombres sueltos: todo Name que no sea parte de p.x, d.x.v ni de una llamada.
    for nodo in _nombres_sueltos(arbol.body):
        if nodo.id in ('p', 'd'):
            raise ErrorExpresion(f'«{texto}»: «{nodo.id}» solo se usa como {nodo.id}.<nombre>')
        if nodo.id in FUNCIONES:
            raise ErrorExpresion(f'«{texto}»: {nodo.id} solo se usa como llamada')
        if nodo.id.startswith('_') or not _ID.match(nodo.id):
            raise ErrorExpresion(f'«{texto}»: el nombre «{nodo.id}» no es válido')
        nombres.add(nodo.id)
    return Analisis(texto, arbol, nombres, parametros, distribuciones)


def _validar_atributo(nodo, texto, parametros, distribuciones):
    base = nodo.value
    if isinstance(base, ast.Name) and base.id == 'p':
        parametros.add(nodo.attr)
        return
    if (isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name) and base.value.id == 'd'):
        distribuciones.add((base.attr, nodo.attr))
        return
    if isinstance(base, ast.Name) and base.id == 'd':
        return  # d.x sin valor: lo rechaza el nivel de arriba si no hay .v
    raise ErrorExpresion(f'«{texto}»: solo se permiten p.<parámetro> y d.<distribución>.<valor>')


def _nombres_sueltos(nodo):
    """Recorre el árbol y devuelve los Name que no son base de p./d. ni función de una llamada."""
    salida = []

    def rec(n):
        if isinstance(n, ast.Attribute):
            base = n.value
            if isinstance(base, ast.Name) and base.id == 'p':
                return
            if (isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name)
                    and base.value.id == 'd'):
                return
            if isinstance(base, ast.Name) and base.id == 'd':
                raise ErrorExpresion('d.<distribución> necesita también .<valor>')
            rec(base)
            return
        if isinstance(n, ast.Call):
            for a in n.args:
                rec(a)
            return
        if isinstance(n, ast.Name):
            salida.append(n)
            return
        for hijo in ast.iter_child_nodes(n):
            rec(hijo)

    rec(nodo)
    return salida


class _Traductor(ast.NodeTransformer):
    """Reescribe nombres: locales → variable con prefijo (o L['x']); el resto → u['x']; p.x → P['x']."""

    def __init__(self, locales, prefijo, atributos, contenedor_locales=None):
        self.locales = locales
        self.prefijo = prefijo
        self.atributos = atributos
        self.contenedor = contenedor_locales

    def _sub(self, contenedor, clave, nodo):
        return ast.copy_location(
            ast.Subscript(value=ast.Name(id=contenedor, ctx=ast.Load()), slice=ast.Constant(clave),
                          ctx=ast.Load()), nodo)

    def visit_Name(self, nodo):
        if nodo.id in FUNCIONES:
            return nodo
        if nodo.id in self.locales:
            if self.contenedor:
                return self._sub(self.contenedor, nodo.id, nodo)
            return ast.copy_location(ast.Name(id=self.prefijo + nodo.id, ctx=ast.Load()), nodo)
        return self._sub(self.atributos, nodo.id, nodo)

    def visit_Attribute(self, nodo):
        base = nodo.value
        if isinstance(base, ast.Name) and base.id == 'p':
            return self._sub('P', nodo.attr, nodo)
        if isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name) and base.value.id == 'd':
            dist = self._sub('D', base.attr, nodo)
            return ast.copy_location(ast.Subscript(value=dist, slice=ast.Constant(nodo.attr),
                                                   ctx=ast.Load()), nodo)
        return self.generic_visit(nodo)


def a_python(analisis, locales=(), prefijo='l_', atributos='u', contenedor_locales=None):
    """Código Python equivalente a la expresión, para el generador de funciones."""
    trad = _Traductor(set(locales), prefijo, atributos, contenedor_locales)
    arbol = trad.visit(copy.deepcopy(analisis.arbol.body))
    ast.fix_missing_locations(arbol)
    return '(' + ast.unparse(arbol) + ')'


ENTORNO = {'__builtins__': {}, 'min': min, 'max': max}


def compilar(texto, locales=(), atributos='u'):
    """Una función f(u, P, D, L) que evalúa la expresión; L guarda los locales (si los hay)."""
    cuerpo = a_python(analizar(texto), locales, atributos=atributos, contenedor_locales='L')
    codigo = f'lambda {atributos}, P, D, L: {cuerpo}'
    return eval(compile(codigo, f'<expresión: {texto}>', 'eval'), dict(ENTORNO))


# --------------------------------------------------------------------------------------------
# Plantillas de texto: «llega a {ruta}». Cada {…} es una expresión; {{ y }} escriben llaves.
# --------------------------------------------------------------------------------------------
def partes_plantilla(texto):
    """Divide una plantilla en [('lit', s) | ('expr', s)]."""
    if not isinstance(texto, str):
        raise ErrorExpresion(f'plantilla de tipo no válido: {texto!r}')
    partes, buf, i, n = [], [], 0, len(texto)
    while i < n:
        c = texto[i]
        if c == '{' and i + 1 < n and texto[i + 1] == '{':
            buf.append('{')
            i += 2
            continue
        if c == '}' and i + 1 < n and texto[i + 1] == '}':
            buf.append('}')
            i += 2
            continue
        if c == '{':
            j, comilla = i + 1, None
            while j < n:
                cj = texto[j]
                if comilla:
                    if cj == comilla:
                        comilla = None
                elif cj in ('"', "'"):
                    comilla = cj
                elif cj == '}':
                    break
                j += 1
            if j >= n:
                raise ErrorExpresion(f'plantilla sin cerrar: «{texto}»')
            if buf:
                partes.append(('lit', ''.join(buf)))
                buf = []
            partes.append(('expr', texto[i + 1:j]))
            i = j + 1
            continue
        if c == '}':
            raise ErrorExpresion(f'«}}» suelta en la plantilla «{texto}» (usa «}}}}»)')
        buf.append(c)
        i += 1
    if buf:
        partes.append(('lit', ''.join(buf)))
    return partes


def analizar_plantilla(texto):
    """Valida la plantilla; devuelve (partes, nombres, parametros, distribuciones)."""
    partes = []
    nombres, parametros, distribuciones = set(), set(), set()
    for tipo, s in partes_plantilla(texto):
        if tipo == 'lit':
            partes.append(('lit', s))
        else:
            a = analizar(s)
            nombres |= a.nombres
            parametros |= a.parametros
            distribuciones |= a.distribuciones
            partes.append(('expr', a))
    return partes, nombres, parametros, distribuciones


def plantilla_a_python(texto, locales=(), prefijo='l_', atributos='u'):
    """Código Python que arma el texto de la plantilla."""
    partes, *_ = analizar_plantilla(texto)
    if not partes:
        return "''"
    trozos = []
    for tipo, x in partes:
        if tipo == 'lit':
            trozos.append(repr(x))
        else:
            trozos.append('_s(' + a_python(x, locales, prefijo, atributos) + ')')
    return trozos[0] if len(trozos) == 1 and partes[0][0] == 'lit' else '(' + ' + '.join(trozos) + ')'

