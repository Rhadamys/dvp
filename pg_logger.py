# Online Python Tutor
# https://github.com/pgbovine/OnlinePythonTutor/
#
# Copyright (C) Philip J. Guo (philip@pgbovine.net)
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


# This is the meat of the Online Python Tutor back-end.  It implements a
# full logger for Python program execution (based on pdb, the standard
# Python debugger imported via the bdb module), printing out the values
# of all in-scope data structures after each executed instruction.

# NB: try to import the minimal amount of stuff in this module to lessen
# the security attack surface

import imp
import sys
import bdb # the KEY import here!
import re
import traceback
import types
import copy

# TODO: use the 'six' package to smooth out Py2 and Py3 differences
is_python3 = (sys.version_info[0] == 3)

# NB: don't use cStringIO since it doesn't support unicode!!!
if is_python3:
    import io as StringIO
    import io # expose regular io for Python3 users too
else:
    import StringIO
import pg_encoder

BINARY_LOGICALS = ['and', 'or', '&', '|', 'in', 'not in', 'not_in']
UNARY_LOGICALS = ['not', '~']
LOGICALS = BINARY_LOGICALS + UNARY_LOGICALS

LOGICAL_OPERATORS = ['<', '<=', '>=', '>', '==', '!=', '=']
MATH_OPERATORS = [ '+', '-' '*', '/', '**', '//', '%']
OPERATORS = LOGICAL_OPERATORS + MATH_OPERATORS

DEBUG = True # Para imprimir las excepciones en la consola
# upper-bound on the number of executed lines, in order to guard against
# infinite loops
MAX_EXECUTED_LINES = 1000 # on 2016-05-01, I increased the limit from 300 to 1000 for Python due to popular user demand! and I also improved the warning message
MAX_RECURSIVE_CALLS = 100

# Mensajes
MAX_EXECUTED_LINES_REACHED = '''Actualmente se pueden ejecutar hasta {0} pasos.
Por favor, considera:<ul><li>Disminuir el largo del código</li>
<li><b>¿Habrá un loop infinito?</b></li></ul>'''
MAX_RECURSIVE_CALLS_REACHED = '''La función <u>{0}</u> se ha llamado {1} veces sin 
retornar algún valor. Por favor, comprueba que no hayan <u>llamados 
recursivos</u> que impidan retornar un valor. Aquí algunos ejemplos:
<div class="md-layout md-gutter" style="margin-top: 12px; margin-bottom: 12px;"> <div class="md-layout-item"> <div class="md-card" style="margin-bottom: 12px;"> <div class="md-card-content code"> <div class="code-line"> <div class="code-reserved">def </div><div class="code-identifier">funcionRecursiva</div><div>(res):</div></div><div class="code-line"><div class="code-indent"></div><div>...</div></div><div class="code-line"> <div class="code-indent"></div><div class="code-reserved">if </div><div>res == </div><div class="code-num">1</div><div>:</div></div><div class="code-line"> <div class="code-indent"></div><div class="code-indent"></div><div class="code-reserved">return </div><div class="code-num">1</div></div><div class="code-line"> <div class="code-indent"></div><div class="code-reserved">else</div><div>:</div></div><div class="code-line"> <div class="code-indent"></div><div class="code-indent"></div><div class="code-reserved">return </div><div>funcionRecursiva(res - </div><div class="code-num">1</div><div>)</div></div><div class="code-line"></div><div class="code-line"> <div>funcionRecursiva(</div><div class="code-num">{1}</div><div>)</div></div></div></div></div><div class="md-layout-item"> <div class="md-card"> <div class="md-card-content code"> <div class="code-line"> <div class="code-reserved">def </div><div class="code-identifier">funcionA</div><div>():</div></div><div class="code-line"><div class="code-indent"></div><div>...</div></div><div class="code-line"> <div class="code-indent"></div><div>funcionB()</div></div><div class="code-line"></div><div class="code-line"> <div class="code-reserved">def </div><div class="code-identifier">funcionB</div><div>():</div></div><div class="code-line"><div class="code-indent"></div><div>...</div></div><div class="code-line"> <div class="code-indent"></div><div>funcionA()</div></div><div class="code-line"></div><div class="code-line"> </div><div>funcionA()</div></div></div></div></div></div>
Si has generado estos llamados recursivos a propósito, por favor 
considera <u>disminuir el tamaño de la entrada</u> para no superar 
este límite.'''
OPEN_NOT_SUPPORTED = '''Aún no se puede utilizar open().
Puedes utilizar {0} para simular 
un archivo.'''

BREAKPOINT_STR = '#break'

# if a line starts with this string, then look for a comma-separated
# list of variables after the colon. *hide* those variables in da trace
#
# 2018-06-17:
# - now supports unix-style shell globs using the syntax in
#   https://docs.python.org/3/library/fnmatch.html so you can write things
#   like '#pythontutor_hide: _*' to hide all private instance variables
# - also now filters class and instance fields in addition to top-level vars
PYTUTOR_HIDE_STR = '#pythontutor_hide:'
# 2018-06-17: a comma-separated list of types that should be displayed *inline*
# like primitives, with their actual values HIDDEN to save space. for details
# of what types are legal to specify, see:
# pg_encoder.py:should_inline_object_by_type()
# - also accepts shell globs, just like PYTUTOR_HIDE_STR
PYTUTOR_INLINE_TYPE_STR = '#pythontutor_hide_type:'

CLASS_RE = re.compile('class\s+')

# copied-pasted from translate() in https://github.com/python/cpython/blob/2.7/Lib/fnmatch.py
def globToRegex(pat):
    """Translate a shell PATTERN to a regular expression.
    There is no way to quote meta-characters.
    """

    i, n = 0, len(pat)
    res = ''
    while i < n:
        c = pat[i]
        i = i+1
        if c == '*':
            res = res + '.*'
        elif c == '?':
            res = res + '.'
        elif c == '[':
            j = i
            if j < n and pat[j] == '!':
                j = j+1
            if j < n and pat[j] == ']':
                j = j+1
            while j < n and pat[j] != ']':
                j = j+1
            if j >= n:
                res = res + '\\['
            else:
                stuff = pat[i:j].replace('\\','\\\\')
                i = j+1
                if stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                elif stuff[0] == '^':
                    stuff = '\\' + stuff
                res = '%s[%s]' % (res, stuff)
        else:
            res = res + re.escape(c)
    return res + '\Z(?ms)'

def compileGlobMatch(pattern):
    # very important to use match and *not* search!
    return re.compile(globToRegex(pattern)).match

# simple sandboxing scheme:
#
# - use resource.setrlimit to deprive this process of ANY file descriptors
#   (which will cause file read/write and subprocess shell launches to fail)
# - restrict user builtins and module imports
#   (beware that this is NOT foolproof at all ... there are known flaws!)
#
# ALWAYS use defense-in-depth and don't just rely on these simple mechanisms
try:
    import resource
    resource_module_loaded = True
except ImportError:
    # Google App Engine doesn't seem to have the 'resource' module
    resource_module_loaded = False


# From http://coreygoldberg.blogspot.com/2009/05/python-redirect-or-turn-off-stdout-and.html
class NullDevice():
    def write(self, s):
        pass


# ugh, I can't figure out why in Python 2, __builtins__ seems to
# be a dict, but in Python 3, __builtins__ seems to be a module,
# so just handle both cases ... UGLY!
if type(__builtins__) is dict:
    BUILTIN_IMPORT = __builtins__['__import__']
else:
    assert type(__builtins__) is types.ModuleType
    BUILTIN_IMPORT = __builtins__.__import__


# whitelist of module imports
ALLOWED_STDLIB_MODULE_IMPORTS = ('math', 'random', 'time', 'datetime',
                          'functools', 'itertools', 'operator', 'string',
                          'collections', 're', 'json',
                          'heapq', 'bisect', 'copy', 'hashlib', 'typing',
                          # the above modules were first added in 2012-09
                          # and then incrementally appended to up until
                          # 2016-ish (see git blame logs)

                          # added these additional ones on 2018-06-15
                          # after seeing usage logs of what users tried
                          # importing a lot but we didn't support yet
                          # (ignoring imports that heavily deal with
                          # filesystem, networking, or 3rd-party libs)
                          '__future__', 'cmath', 'decimal', 'fractions',
                          'pprint', 'calendar', 'pickle',
                          'types', 'array',
                          'locale', 'abc',
                          'doctest', 'unittest',
                          )

# allow users to import but don't explicitly import it since it's
# already been done above
OTHER_STDLIB_WHITELIST = ('StringIO', 'io')


# Restrict imports to a whitelist
def __restricted_import__(*args):
    # filter args to ONLY take in real strings so that someone can't
    # subclass str and bypass the 'in' test on the next line
    args = [e for e in args if type(e) is str]

    all_allowed_imports = sorted(ALLOWED_STDLIB_MODULE_IMPORTS + OTHER_STDLIB_WHITELIST)
    if is_python3:
        all_allowed_imports.remove('StringIO')
    else:
        all_allowed_imports.remove('typing')

    if args[0] in all_allowed_imports:
        imported_mod = BUILTIN_IMPORT(*args)
        # somewhat weak protection against imported modules that contain one
        # of these troublesome builtins. again, NOTHING is foolproof ...
        # just more defense in depth :)
        #
        # unload it so that if someone attempts to reload it, then it has to be
        # loaded from the filesystem, which is (supposedly!) blocked by setrlimit
        for mod in ('os', 'sys', 'posix', 'gc'):
            if hasattr(imported_mod, mod):
                delattr(imported_mod, mod)

        return imported_mod
    else:
        # original error message ...
        #raise ImportError('{0} not supported'.format(args[0]))

        # 2017-12-06: added a better error message to tell the user what
        # modules *can* be imported in python tutor ...
        ENTRIES_PER_LINE = 6

        lines_to_print = []
        # adapted from https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
        for i in range(0, len(all_allowed_imports), ENTRIES_PER_LINE):
            lines_to_print.append(all_allowed_imports[i:i + ENTRIES_PER_LINE])
        pretty_printed_imports = ',\n  '.join([', '.join(e) for e in lines_to_print])

        raise ImportError('El módulo {0} no se ha encontrado o no está soportado actualmente.\nSólo se pueden importar estos módulos:\n  {1}'.format(args[0], pretty_printed_imports))


# Support interactive user input by:
#
# 1. running the entire program up to a call to raw_input (or input in py3),
# 2. bailing and returning a trace ending in a special 'raw_input' event,
# 3. letting the web frontend issue a prompt to the user to grab a string,
# 4. RE-RUNNING the whole program with that string added to input_string_queue,
# 5. which should bring execution to the next raw_input call (if
#    available), or to termination.
# Repeat until no more raw_input calls are encountered.
# Note that this is mad inefficient, but is simple to implement!

# VERY IMPORTANT -- set random seed to 0 to ensure deterministic execution:
import random
random.seed(0)

# queue of input strings passed from either raw_input or mouse_input
input_string_queue = []


def open_wrapper(*args):
    if is_python3:
        raise Exception(OPEN_NOT_SUPPORTED.format('io.StringIO()'))
    else:
        raise Exception(OPEN_NOT_SUPPORTED.format('StringIO.StringIO()'))

# create a more sensible error message for unsupported features
def create_banned_builtins_wrapper(fn_name):
    def err_func(*args):
        raise Exception("'" + fn_name + "' is not supported by Python Tutor.")
    return err_func

class RawInputException(Exception):
    pass

def raw_input_wrapper(prompt=''):
    if input_string_queue:
        input_str = input_string_queue.pop(0)

        # write the prompt and user input to stdout, to emulate what happens
        # at the terminal
        sys.stdout.write(str(prompt)) # always convert prompt into a string
        sys.stdout.write(input_str + "\n") # newline to simulate the user hitting Enter
        return input_str
    raise RawInputException(str(prompt)) # always convert prompt into a string


# Python 2 input() does eval(raw_input())
def python2_input_wrapper(prompt=''):
    if input_string_queue:
        input_str = input_string_queue.pop(0)

        # write the prompt and user input to stdout, to emulate what happens
        # at the terminal
        sys.stdout.write(str(prompt)) # always convert prompt into a string
        sys.stdout.write(input_str + "\n") # newline to simulate the user hitting Enter
        return eval(input_str) # remember to eval!
    raise RawInputException(str(prompt)) # always convert prompt into a string

class MouseInputException(Exception):
    pass

def mouse_input_wrapper(prompt=''):
    if input_string_queue:
        return input_string_queue.pop(0)
    raise MouseInputException(prompt)


# blacklist of builtins
BANNED_BUILTINS = [] # 2018-06-15 don't ban any builtins since that's just security by obscurity
                     # we should rely on other layered security mechanisms

# old banned built-ins prior to 2018-06-15
#BANNED_BUILTINS = ['reload', 'open', 'compile',
#                   'file', 'eval', 'exec', 'execfile',
#                   'exit', 'quit', 'help',
#                   'dir', 'globals', 'locals', 'vars']
# Peter says 'apply' isn't dangerous, so don't ban it

IGNORE_VARS = set(('__builtins__', '__name__', '__exception__', '__doc__', '__package__'))

# at_global_scope should be true only if 'frame' represents the global scope
def get_user_globals(frame, at_global_scope=False):
    d = filter_var_dict(frame.f_globals)

    # don't blurt out all of f_valuestack for now ...
    '''
    if at_global_scope and hasattr(frame, 'f_valuestack'):
      for (i, e) in enumerate(frame.f_valuestack):
        d['_tmp' + str(i+1)] = e
    '''

    # print out list objects being built up in Python 2.x list comprehensions
    # (which don't have its own special <listcomp> frame, sadly)
    if not is_python3 and hasattr(frame, 'f_valuestack'):
        for (i, e) in enumerate([e for e in frame.f_valuestack if type(e) is list]):
            d['_tmp' + str(i+1)] = e

    # also filter out __return__ for globals only, but NOT for locals
    if '__return__' in d:
        del d['__return__']
    return d

def get_user_locals(frame):
    ret = filter_var_dict(frame.f_locals)
    # don't blurt out all of f_valuestack for now ...
    '''
    if hasattr(frame, 'f_valuestack'):
      for (i, e) in enumerate(frame.f_valuestack):
        ret['_tmp' + str(i+1)] = e
    '''

    # special printing of list/set/dict comprehension objects as they are
    # being built up incrementally ...
    f_name = frame.f_code.co_name
    if hasattr(frame, 'f_valuestack'):
        # print out list objects being built up in Python 2.x list comprehensions
        # (which don't have its own special <listcomp> frame, sadly)
        if not is_python3:
            for (i, e) in enumerate([e for e in frame.f_valuestack
                                     if type(e) is list]):
                ret['_tmp' + str(i+1)] = e

        # for dict and set comprehensions, which have their own frames:
        if f_name.endswith('comp>'):
            for (i, e) in enumerate([e for e in frame.f_valuestack
                                     if type(e) in (list, set, dict)]):
                ret['_tmp' + str(i+1)] = e

    return ret

def filter_var_dict(d):
    ret = {}
    for (k,v) in d.items():
        if k not in IGNORE_VARS:
            ret[k] = v
    return ret


# yield all function objects locally-reachable from frame,
# making sure to traverse inside all compound objects ...
def visit_all_locally_reachable_function_objs(frame):
    for (k, v) in get_user_locals(frame).items():
        for e in visit_function_obj(v, set()):
            if e: # only non-null if it's a function object
                assert type(e) in (types.FunctionType, types.MethodType)
                yield e


# TODO: this might be slow if we're traversing inside lots of objects:
def visit_function_obj(v, ids_seen_set):
    v_id = id(v)

    # to prevent infinite loop
    if v_id in ids_seen_set:
        yield None
    else:
        ids_seen_set.add(v_id)

        typ = type(v)

        # simple base case
        if typ in (types.FunctionType, types.MethodType):
            yield v

        # recursive cases
        elif typ in (list, tuple, set):
            for child in v:
                for child_res in visit_function_obj(child, ids_seen_set):
                    yield child_res

        elif typ == dict or pg_encoder.is_class(v) or pg_encoder.is_instance(v):
            contents_dict = None

            if typ == dict:
                contents_dict = v
            # warning: some classes or instances don't have __dict__ attributes
            elif hasattr(v, '__dict__'):
                contents_dict = v.__dict__

            if contents_dict:
                for (key_child, val_child) in contents_dict.items():
                    for key_child_res in visit_function_obj(key_child, ids_seen_set):
                        yield key_child_res
                    for val_child_res in visit_function_obj(val_child, ids_seen_set):
                        yield val_child_res

        # degenerate base case
        yield None


class PGLogger(bdb.Bdb):
        # if custom_modules is non-empty, it should be a dict mapping module
        # names to the python source code of each module. when _runscript is
        # called, it will do "from <module> import *" for all modules in
        # custom_modules before running the user's script and then trace all
        # code within custom_modules
        #
        # if separate_stdout_by_module, then have a separate stdout stream
        # for each module rather than all stdout going to a single stream
    def __init__(self, cumulative_mode, heap_primitives, show_only_outputs,
                 disable_security_checks=False, allow_all_modules=False, crazy_mode=False,
                 custom_modules=None, separate_stdout_by_module=False, probe_exprs=None):
        bdb.Bdb.__init__(self)
        self.mainpyfile = ''
        self._wait_for_mainpyfile = 0

        if probe_exprs:
            self.probe_exprs = probe_exprs
        else:
            self.probe_exprs = None

        self.separate_stdout_by_module = separate_stdout_by_module
        self.stdout_by_module = {} # Key: module name, Value: StringIO faux-stdout

        self.modules_to_trace = set(['__main__']) # always trace __main__!

        # Key: module name
        # Value: module's python code as a string
        self.custom_modules = custom_modules
        if self.custom_modules:
            for module_name in self.custom_modules:
                self.modules_to_trace.add(module_name)

        self.disable_security_checks = disable_security_checks
        self.allow_all_modules = allow_all_modules
        # if we allow all modules, we shouldn't do security checks
        # either since otherwise users can't really import anything
        # because that will likely involve opening files on disk, which
        # is disallowed by security checks
        if self.allow_all_modules:
            self.disable_security_checks = True

        # if True, then displays ALL stack frames that have ever existed
        # rather than only those currently on the stack (and their
        # lexical parents)
        self.cumulative_mode = cumulative_mode

        # if True, then render certain primitive objects as heap objects
        self.render_heap_primitives = heap_primitives

        # if True, then don't render any data structures in the trace,
        # and show only outputs
        self.show_only_outputs = show_only_outputs

        # Run using the custom Py2crazy Python interpreter
        self.crazy_mode = crazy_mode

        # each entry contains a dict with the information for a single
        # executed line
        self.trace = []

        # if this is true, don't put any more stuff into self.trace
        self.done = False

        # if this is non-null, don't do any more tracing until a
        # 'return' instruction with a stack gotten from
        # get_stack_code_IDs() that matches wait_for_return_stack
        self.wait_for_return_stack = None

        #http://stackoverflow.com/questions/2112396/in-python-in-google-app-engine-how-do-you-capture-output-produced-by-the-print
        self.GAE_STDOUT = sys.stdout
        self.ORIGINAL_STDERR = sys.stderr

        # Key:   function object
        # Value: parent frame
        self.closures = {}

        # Key:   code object for a lambda
        # Value: parent frame
        self.lambda_closures = {}

        # set of function objects that were defined in the global scope
        self.globally_defined_funcs = set()

        # Key: frame object
        # Value: monotonically increasing small ID, based on call order
        self.frame_ordered_ids = {}
        self.cur_frame_id = 1

        # List of frames to KEEP AROUND after the function exits.
        # If cumulative_mode is True, then keep ALL frames in
        # zombie_frames; otherwise keep only frames where
        # nested functions were defined within them.
        self.zombie_frames = []

        # set of elements within zombie_frames that are also
        # LEXICAL PARENTS of other frames
        self.parent_frames_set = set()

        # all globals that ever appeared in the program, in the order in
        # which they appeared. note that this might be a superset of all
        # the globals that exist at any particular execution point,
        # since globals might have been deleted (using, say, 'del')
        self.all_globals_in_order = []

        # very important for this single object to persist throughout
        # execution, or else canonical small IDs won't be consistent.
        self.encoder = pg_encoder.ObjectEncoder(self)

        self.executed_script = None # Python script to be executed!

        # if there is at least one line that ends with BREAKPOINT_STR,
        # then activate "breakpoint mode", where execution should stop
        # ONLY at breakpoint lines.
        self.breakpoints = []

        self.vars_to_hide = set() # a set of regex match objects
                                  # created by compileGlobMatch() from
                                  # the contents of PYTUTOR_HIDE_STR
        self.types_to_inline = set() # a set of regex match objects derived from PYTUTOR_INLINE_TYPE_STR

        self.prev_lineno = -1 # keep track of previous line just executed

        self.registered_loops = dict(stack=[]) # Loops registrados

    def register_loop(self, line):
        """
        Registra un nuevo loop. De esta forma se le puede hacer seguimiento
        a su ejecución para ver, por ejemplo, qué operaciones se realizan dentro
        y fuera de un ciclo.

        Returns:
            bool: True, si ya se registró este loop y necesita actualizarse.
        """
        if line.startswith('for'):
            line_parts = line.strip(':').split(' ')
            line_parts = list(filter(None, line_parts))
            iterable_idx = line_parts.index('in') + 1
            iterable_str = ' '.join(line_parts[iterable_idx:])
            iterable_val = eval(iterable_str, self.user_globals, self.user_locals)
            iterable = list(iterable_val)
            loop = dict(iterable=iterable)
        else:
            conditional = self.trace_conditional(line)
            line_parts = conditional['expression'].split(' ')
            line_parts = list(filter(None, line_parts))
            line_parts.insert(0, 'while')
            loop = dict(conditional=conditional)
            
        loop_type = line_parts[0]
        loop.update(dict(line=self.lineno,
                         type=loop_type,
                         line_parts=line_parts,
                         current=0))
        self.registered_loops[self.lineno] = loop
        self.registered_loops['stack'].append(self.lineno)
        return copy.deepcopy(loop)

    def update_loop(self):
        """ 
        Actualiza la información del loop actual, tales como el ciclo en que
        va. Si es un for, también actualiza el elemento iterable.
        TODO: En el front, animaciones para for?

        Returns:
            any: Devuelve el objeto del loop si éste ya terminó, porque no se agrega
                al stack de salida en la traza.
        """
        loop = self.registered_loops[self.lineno]
        loop_type = loop['type']
        loop['current'] += 1

        if loop_type == 'for':
            iterable = loop['line_parts'][-1]
            iterable = eval(iterable, self.user_globals, self.user_locals)
            loop['iterable'] = list(iterable)
            last = len(loop['iterable']) - 1
            if loop['current'] > last:
                del self.registered_loops[self.lineno]
                self.registered_loops['stack'].pop()
        else:
            expression = loop['conditional']['expression']
            conditional = self.trace_conditional(expression)
            if not conditional['result']:
                del self.registered_loops[self.lineno]
                self.registered_loops['stack'].pop()
            loop['conditional'] = conditional
        return copy.deepcopy(loop)

    def trace_conditional(self, line):
        start = end = self.lineno
        if line.startswith('if'):
            line = line[2:]
        elif line.startswith('elif'):
            line = line[4:]
        elif line.startswith('while'):
            line = line[5:]

        line = line.strip(':').strip()
        if line.endswith('\\') or (line.startswith('(') and not line.endswith(')')):
            line = line.strip('\\')
            end_found = False
            while(not end_found):
                current = self.executed_script_lines[end].strip().strip('\\')
                if current.endswith(':'):
                    current = current.strip(':')
                    end_found = True
                line += current
                end += 1

        if line.startswith('(') and line.endswith(')'):
            line = line[1 : -1]
        
        global_scope = self.current_stack['global']
        list_vars = global_scope['ordered_varnames']
        scope_name = self.current_stack['ordered_scopes'][-1]
        in_local_scope = not scope_name == 'global'
        if in_local_scope:
            local_scope = self.current_stack[scope_name]
            last_hash = local_scope['ordered_hashes'][-1]
            local_scope = local_scope[last_hash]
            local_vars = local_scope['ordered_varnames']
            for varname in local_vars:
                if not varname in list_vars:
                    list_vars.append(varname)

        # Para render: determina el tipo de una parte de la expresión para
        # poder colorearla en el front.
        def encode_part(part):
            v_type = type(part)
            ret = dict()
            if v_type == bool:
                v_type = part
                part = str(part)
            elif v_type == int or v_type == float:
                v_type = 'number'
            elif part == '?':
                v_type = 'or-skipped'
            elif '(' in part:
                v_type = 'function'
                result = eval(part, self.user_globals, self.user_locals)
                n_part = part.replace('(', ',').strip(')').strip(' ').split(',')
                part = n_part.pop(0)
                params = []
                for p in n_part:
                    params.append(encode_part(p))
                ret.update(dict(params=params, result=result))
            elif part.startswith(("'", '"')):
                v_type = 'string'
            elif part in OPERATORS:
                v_type = 'operator'
            elif part in LOGICALS:
                v_type = 'logical'
            else:
                v_type = 'unknown'
            ret.update(dict(part=part, type=v_type))
            return ret

        def search_var_value(subexp):
            regx = re.compile('\\b(' + '|'.join(list_vars) + ')\\b')
            part = subexp['part']
            without_str = re.sub(r'(["\'])(\\?.)*?\1', '', part)
            for found in regx.finditer(without_str):
                varname = found.group()
                value = local_scope['encoded_vars'][varname] if in_local_scope and varname in local_scope['encoded_vars'] else global_scope['encoded_vars'][varname]

                if '[' in part:
                    print(part, file=self.GAE_STDOUT, end="\n\n")
                    part = part.replace(']', '').split('[')
                    variable = eval(part[0], self.user_globals, self.user_locals)
                    part = part[1:]
                    for index in part:
                        try:
                            index = int(index) + 1
                            value = value[index]
                        except ValueError:
                            if ':' in index:
                                print(index, file=self.GAE_STDOUT, end="\n\n")
                                colon = index.count(':')
                                indexes = index.split(':' * colon)

                                print(indexes, file=self.GAE_STDOUT, end="\n\n")
                                if len(indexes[0]) == 0:
                                    indexes[0] = 'None'
                                indexes[0] = eval(indexes[0], self.user_globals, self.user_locals)

                                if len(indexes[1]) == 0:
                                    indexes[1] = 'None'
                                indexes[1] = eval(indexes[1], self.user_globals, self.user_locals)
                                print(indexes, file=self.GAE_STDOUT, end="\n\n")
                                if colon == 1:
                                    value = value[indexes[0]:indexes[1]]
                                else:
                                    value = value[indexes[0]::indexes[1]]
                            elif '$' in index:
                                dictionary = copy.deepcopy(value)
                                dictionary.pop(0)
                                index = index[1 : -1]
                                for item in dictionary:
                                    if item[0] == index:
                                        value = item[1]
                            else:
                                index = eval(index, self.user_globals, self.user_locals)
                                value = value[index]
                subexp.update(dict(type='variable', value=value))
        
        def decompose_expression(expression):
            NOT_A_FUNCTION = LOGICALS + OPERATORS
            ADD_SPACE = NOT_A_FUNCTION + ['(', ')', '[', ']']
            for exp in ADD_SPACE:
                if exp.isalpha():
                    expression = re.sub(r'\b' + re.escape(exp) + r'\b', ' ' + exp + ' ', expression)
                else:
                    expression = expression.replace(exp, ' ' + exp + ' ')

            # Rearmar operandos
            REBUILD = [r'<[\s]*=', r'>[\s]*=', r'=[\s]*=', r'![\s]*=',  r'/[\s]*/', r'\*[\s]*\*', r'not[\s]{1,}in']
            RE_REPLACE = ['<=', '>=', '==', '!=', '//', '**', 'not_in']
            for i in range(len(REBUILD)):
                expression = re.sub(REBUILD[i], RE_REPLACE[i], expression)
            expression = expression.split(' ')
            expression = list(filter(None, expression))
            parsed = ' '.join(expression)
            print('---\n', parsed, file=self.GAE_STDOUT, end="\n\n")

            # Juntar llamados de funciones
            temp = []
            while expression:
                part = expression.pop(0)
                if expression:
                    if not(part in NOT_A_FUNCTION or part[0].isdigit()) and (expression[0] == '(' or expression[0] == '['):
                        bracket = expression[0] == '('
                        part += expression.pop(0)
                        if bracket:
                            while((bracket and not expression[0] == ')')): # Es ( y aún no encuentra )
                                part += expression.pop(0) + ' '
                        else:
                            while(not bracket and (not expression[0] == ']' or # es [ y aún no encuentra ]
                                (len(expression) > 1 and expression[1] == '['))): # o hay un nuevo [
                                part += expression.pop(0)
                        part = part.strip() + expression.pop(0)
                    elif part == 'not' and expression[0] == 'in':
                        part += expression.pop(0)
                temp.append(part)
            
            expression = temp
            def search_parenthesis_expr(expression):
                parsed = []
                parsed_part = ''
                encoded = []
                encoded_part = dict()
                while expression:
                    part = expression.pop(0)
                    if part == '(':
                        part, enc = search_parenthesis_expr(expression)
                        parsed.append(part)
                        encoded.append(enc)
                    elif part == ')':
                        if parsed_part:
                            parsed.append(parsed_part)
                            encoded.append(encoded_part)
                        return parsed, encoded
                    elif part in LOGICALS or part in LOGICAL_OPERATORS:
                        if part == 'not_in':
                            part = 'not in'

                        if parsed_part:
                            parsed.append(parsed_part)
                            encoded.append(encoded_part)
                        parsed_part = ''
                        parsed.append(part)

                        encoded_part = dict()
                        enc_part = encode_part(part)
                        encoded.append(enc_part)
                    else:
                        parsed_part += ' ' + part if parsed_part else part

                        enc_part = encode_part(part)
                        encoded_part.update({ len(encoded_part): enc_part })
                if parsed_part:
                    parsed.append(parsed_part)
                    encoded.append(encoded_part)
                return parsed, encoded

            expression, encoded = search_parenthesis_expr(expression)
            return expression, encoded, parsed

        expression, encoded, parsed = decompose_expression(line)
        def eval_expression(exp, enc, trace, tree):
            def eval_subexpression(exp, enc, index):
                index_first = index
                index_operator = index + 1
                index_second = index + 2

                first = eval_expression(exp[index_first], enc[index_first], trace, '{0}{1}>'.format(tree, index_first))
                if index_operator >= len(exp) - 1 or exp[index_operator] not in LOGICAL_OPERATORS:
                    enc_copy = copy.deepcopy(encoded)
                    exp[index_first] = first
                    enc[index_first] = encode_part(first)
                    return first, enc_copy, False

                operator = exp[index_operator]
                second = eval_expression(exp[index_second], enc[index_second], trace, '{0}{1}>'.format(tree, index_second))
                to_eval = '{0} {1} {2}'.format(first, operator, second)
                result = eval(to_eval, self.user_globals, self.user_locals)
                enc_copy = copy.deepcopy(encoded)
                del exp[index + 1 : index + 3]
                del enc[index + 1 : index + 3]
                exp[index_first] = result
                enc[index_first] = encode_part(result)
                return result, enc_copy, True

            def update_trace(enc, result, tree):
                entry = dict(expression=enc, 
                             result=result,
                             tree=tree)
                trace.append(entry)

            if isinstance(exp, list):
                index = 0
                while index < len(exp):
                    print('---\n', encoded, file=self.GAE_STDOUT, end="\n\n")
                    curr_exp = exp[index]
                    curr_enc = enc[index]
                    curr_tree = tree + str(index)

                    if isinstance(curr_exp, list):
                        result = eval_expression(curr_exp, curr_enc, trace, curr_tree + '>')
                        exp[index] = result
                        enc[index] = encode_part(result)
                    elif curr_exp in UNARY_LOGICALS:
                        next_exp, enc_copy, has_sub = eval_subexpression(exp, enc, index + 1)
                        if has_sub:
                            update_trace(enc_copy, next_exp, tree + str(index + 2))

                        to_eval = '{0} {1}'.format(curr_exp, curr_enc, next_exp)
                        result = eval(to_eval, self.user_globals, self.user_locals)
                        update_trace(copy.deepcopy(encoded), result, curr_tree)
                        exp.pop(index)
                        enc.pop(index)
                        exp[index] = result
                        enc[index] = encode_part(result)
                    elif curr_exp in BINARY_LOGICALS:
                        prev_result = exp[index - 1]
                        if curr_exp == 'or' and prev_result:
                            exp_len = index + 2 < len(exp) - 1
                            if exp_len and exp[index + 2] in LOGICAL_OPERATORS:
                                del exp[index + 2 : index + 4]
                                del enc[index + 2 : index + 4]
                            exp[index + 1] = '?'
                            enc[index + 1] = encode_part('?')
                            result = True
                            update_trace(copy.deepcopy(encoded), result, curr_tree)
                        else:
                            next_exp, enc_copy, has_sub = eval_subexpression(exp, enc, index + 1)
                            if has_sub:
                                update_trace(enc_copy, next_exp, tree + str(index + 2))
                            exp[index + 1] = next_exp
                            enc[index + 1] = encode_part(next_exp)
                            to_eval = '''{0} {1} {2}'''.format(prev_result, curr_exp, next_exp)
                            result = eval(to_eval, self.user_globals, self.user_locals)
                            update_trace(copy.deepcopy(encoded), result, curr_tree)
                        del exp[index : index + 2]
                        del enc[index : index + 2]
                        index = index - 1
                        exp[index] = result
                        enc[index] = encode_part(result)
                    else:
                        result, enc_copy, has_sub = eval_subexpression(exp, enc, index)
                        if has_sub:
                            update_trace(enc_copy, result, tree + str(index + 1))
                    index = index + 1
                ret = exp[0]
                if type(ret) == str:
                    ret = """'{0}'""".format(ret)
                return exp[0]
            else:
                search_var_value(enc[0])
                result = eval(exp, self.user_globals, self.user_locals)
                if type(result) == str:
                    result = """'{0}'""".format(result)
                return result       
        
        trace = []
        res = eval_expression(expression, encoded, trace, '')
        ret = dict(exp_start=start, 
                   exp_ends=end, 
                   expression=parsed,
                   result=res, 
                   trace=trace)
        return ret

    def check_variable_value_changes(self, prev, current):
        """
        Busca cambios de valores en las variables entre los distintos pasos. Si se detecta un
        cambio de valor, el valor anterior se añade al arreglo de valores pasados. De esta forma
        se puede renderizar el valor actual y los anteriores en el front.

        Args:
            prev (obj): Stack del paso anterior.
            current (obj): Stack del paso actual.
        
        Returns:
            obj: Stack del paso actual, con las variables actualizadas de acuerdo a si se encontraron
                o no modificaciones en su valor.
        """
        for varname in current['ordered_varnames']:
            if not varname in prev['ordered_varnames']:
                continue
                
            has_prevals = varname in prev['prev_encoded_vars']
            if has_prevals:
                current['prev_encoded_vars'][varname] = prev['prev_encoded_vars'][varname]

            prev_value = prev['encoded_vars'][varname]
            curr_value = current['encoded_vars'][varname]
            if not curr_value == prev_value:
                prev_record = dict(step=len(self.trace), value=prev_value)
                if has_prevals:
                    current['prev_encoded_vars'][varname].insert(0, prev_record)
                else:
                    current['prev_encoded_vars'][varname] = [prev_record]
        return current

    def should_hide_var(self, var):
        for re_match in self.vars_to_hide:
            if re_match(var):
                return True
        return False


    def get_user_stdout(self):
        def encode_stringio(sio):
            # This is SUPER KRAZY! In Python 2, the buflist inside of a StringIO
            # instance can be made up of both str and unicode, so we need to convert
            # the str to unicode and replace invalid characters with the Unicode '?'
            # But leave unicode elements alone. This way, EVERYTHING inside buflist
            # will be unicode. (Note that in Python 3, everything is already unicode,
            # so we're fine.)
            if not is_python3:
                sio.buflist = [(e.decode('utf-8', 'replace')
                                           if type(e) is str
                                           else e)
                                          for e in sio.buflist]
            return sio.getvalue()

        if self.separate_stdout_by_module:
            ret = {}
            for module_name in self.stdout_by_module:
                ret[module_name] = encode_stringio(self.stdout_by_module[module_name])
            return ret
        else:
            # common case - single stdout stream
            return encode_stringio(self.user_stdout)


    def get_frame_id(self, cur_frame):
        return self.frame_ordered_ids[cur_frame]

    # Returns the (lexical) parent of a function value.
    def get_parent_of_function(self, val):
        if val in self.closures:
            return self.get_frame_id(self.closures[val])
        elif val in self.lambda_closures:
            return self.get_frame_id(self.lambda_closures[val])
        else:
            return None


    # Returns the (lexical) parent frame of the function that was called
    # to create the stack frame 'frame'.
    #
    # OKAY, this is a SUPER hack, but I don't see a way around it
    # since it's impossible to tell exactly which function
    # ('closure') object was called to create 'frame'.
    #
    # The Python interpreter doesn't maintain this information,
    # so unless we hack the interpreter, we will simply have
    # to make an educated guess based on the contents of local
    # variables inherited from possible parent frame candidates.
    def get_parent_frame(self, frame):
        #print >> sys.stderr, 'get_parent_frame: frame.f_code', frame.f_code
        for (func_obj, parent_frame) in self.closures.items():
            # ok, there's a possible match, but let's compare the
            # local variables in parent_frame to those of frame
            # to make sure. this is a hack that happens to work because in
            # Python, each stack frame inherits ('inlines') a copy of the
            # variables from its (lexical) parent frame.
            if func_obj.__code__ == frame.f_code:
                all_matched = True
                for k in frame.f_locals:
            # Do not try to match local names
                    if k in frame.f_code.co_varnames:
                        continue
                    if k != '__return__' and k in parent_frame.f_locals:
                        if parent_frame.f_locals[k] != frame.f_locals[k]:
                            all_matched = False
                            break

                if all_matched:
                    return parent_frame

        for (lambda_code_obj, parent_frame) in self.lambda_closures.items():
            if lambda_code_obj == frame.f_code:
                # TODO: should we do more verification like above?!?
                return parent_frame

        return None


    def lookup_zombie_frame_by_id(self, frame_id):
        # TODO: kinda inefficient
        for e in self.zombie_frames:
            if self.get_frame_id(e) == frame_id:
                return e
        assert False # should never get here


    # unused ...
    #def reset(self):
    #    bdb.Bdb.reset(self)
    #    self.forget()


    def forget(self):
        self.lineno = None
        self.stack = []
        self.curindex = 0
        self.curframe = None

    def setup(self, f, t):
        self.forget()
        self.stack, self.curindex = self.get_stack(f, t)
        self.curframe = self.stack[self.curindex][0]

    # should be a reasonably unique ID to match calls and returns:
    def get_stack_code_IDs(self):
        return [id(e[0].f_code) for e in self.stack]


    # Override Bdb methods

    def user_call(self, frame, argument_list):
        """This method is called when there is the remote possibility
        that we ever need to stop in this function."""
        # TODO: figure out a way to move this down to 'def interaction'
        # or right before self.trace.append ...
        if self.done: return

        if self._wait_for_mainpyfile:
            return
        if self.stop_here(frame):
            # delete __return__ so that on subsequent calls to
            # a generator function, the OLD yielded (returned)
            # value gets deleted from the frame ...
            try:
                del frame.f_locals['__return__']
            except KeyError:
                pass

            self.interaction(frame, None, 'call')

    def user_line(self, frame):
        """This function is called when we stop or break at this line."""
        if self.done: return

        if self._wait_for_mainpyfile:
            if ((frame.f_globals['__name__'] not in self.modules_to_trace) or
                frame.f_lineno <= 0):
            # older code:
            #if (self.canonic(frame.f_code.co_filename) != "<string>" or
            #    frame.f_lineno <= 0):
                return
            self._wait_for_mainpyfile = 0
        self.interaction(frame, None, 'step_line')

    def user_return(self, frame, return_value):
        """This function is called when a return trap is set here."""
        if self.done: return

        frame.f_locals['__return__'] = return_value
        self.interaction(frame, None, 'return')

    def user_exception(self, frame, exc_info):
        """This function is called if an exception occurs,
        but only if we are to stop at or just below this level."""
        if self.done: return

        exc_type, exc_value, exc_traceback = exc_info
        frame.f_locals['__exception__'] = exc_type, exc_value
        if type(exc_type) == type(''):
            exc_type_name = exc_type
        else: exc_type_name = exc_type.__name__

        stack_to_render = self.trace[-1]['stack_to_render'] if self.trace else None
        if exc_type_name == 'RawInputException':
            raw_input_arg = str(exc_value.args[0]) # make sure it's a string so it's JSON serializable!
            self.trace.append(dict(event='raw_input',
                                   prompt=raw_input_arg,
                                   line=self.prev_lineno,
                                   stdout=self.get_user_stdout(),
                                   stack_to_render=stack_to_render))
            self.done = True
        elif exc_type_name == 'MouseInputException':
            mouse_input_arg = str(exc_value.args[0]) # make sure it's a string so it's JSON serializable!
            self.trace.append(dict(event='mouse_input',
                                   prompt=mouse_input_arg,
                                   line=self.prev_lineno,
                                   stdout=self.get_user_stdout(),
                                   stack_to_render=stack_to_render))
            self.done = True
        else:
            self.interaction(frame, exc_traceback, 'exception')

    def get_script_line(self, n):
        return self.executed_script_lines[n-1]

    # General interaction function

    def interaction(self, frame, traceback, event_type):
        self.setup(frame, traceback)
        tos = self.stack[self.curindex]
        top_frame = tos[0]
        self.lineno = tos[1]

        topframe_module = top_frame.f_globals['__name__']

        # don't trace inside of ANY functions that aren't user-written code
        # (e.g., those from imported modules -- e.g., random, re -- or the
        # __restricted_import__ function in this file)
        #
        # empirically, it seems like the FIRST entry in self.stack is
        # the 'run' function from bdb.py, but everything else on the
        # stack is the user program's "real stack"

        # Look only at the "topmost" frame on the stack ...

        # if we're not in a module that we are explicitly tracing, skip:
        # (this comes up in tests/backend-tests/namedtuple.txt)
        if topframe_module not in self.modules_to_trace:
            return
        # also don't trace inside of the magic "constructor" code
        if top_frame.f_code.co_name == '__new__':
            return
        # or __repr__, which is often called when running print statements
        if top_frame.f_code.co_name == '__repr__':
            return

        # don't trace if wait_for_return_stack is non-null ...
        if self.wait_for_return_stack:
            if event_type == 'return' and \
               (self.wait_for_return_stack == self.get_stack_code_IDs()):
                self.wait_for_return_stack = None # reset!
            return # always bail!
        else:
            # Skip all "calls" that are actually class definitions, since
            # those faux calls produce lots of ugly cruft in the trace.
            #
            # NB: Only trigger on calls to functions defined in
            # user-written code (i.e., co_filename == '<string>'), but that
            # should already be ensured by the above check for whether we're
            # in user-written code.
            if event_type == 'call':
                first_lineno = top_frame.f_code.co_firstlineno
                if topframe_module == "__main__":
                    func_line = self.get_script_line(first_lineno)
                elif topframe_module in self.custom_modules:
                    module_code = self.custom_modules[topframe_module]
                    module_code_lines = module_code.splitlines() # TODO: maybe pre-split lines?
                    func_line = module_code_lines[first_lineno-1]
                else:
                    # you're hosed
                    func_line = ''
                #print >> sys.stderr, func_line

                if CLASS_RE.match(func_line.lstrip()): # ignore leading spaces
                    self.wait_for_return_stack = self.get_stack_code_IDs()
                    return


        self.encoder.reset_heap() # VERY VERY VERY IMPORTANT,
                                  # or else we won't properly capture heap object mutations in the trace!

        if event_type == 'call':
            # Don't be so strict about this assertion because it FAILS
            # when you're calling a generator (not for the first time),
            # since that frame has already previously been on the stack ...
            #assert top_frame not in self.frame_ordered_ids

            self.frame_ordered_ids[top_frame] = self.cur_frame_id
            self.cur_frame_id += 1

            if self.cumulative_mode:
                self.zombie_frames.append(top_frame)

        # kinda tricky to get the timing right -- basically, as soon as you
        # make a call, set sys.stdout to the stream for the appropriate
        # module, and as soon as you return, set sys.stdout to the
        # stream for your caller's module. we need to do this on the
        # return call since we want to immediately start picking up
        # prints to stdout *right after* this function returns
        if self.separate_stdout_by_module:
            if event_type == 'call':
                if topframe_module in self.stdout_by_module:
                    sys.stdout = self.stdout_by_module[topframe_module]
                else:
                    sys.stdout = self.stdout_by_module["<other>"]
            elif event_type == 'return' and self.curindex > 0:
                prev_tos = self.stack[self.curindex - 1]
                prev_topframe = prev_tos[0]
                prev_topframe_module = prev_topframe.f_globals['__name__']
                if prev_topframe_module in self.stdout_by_module:
                    sys.stdout = self.stdout_by_module[prev_topframe_module]
                else:
                    sys.stdout = self.stdout_by_module["<other>"]


        # only render zombie frames that are NO LONGER on the stack
        #
        # subtle: self.stack[:self.curindex+1] is the real stack, since
        # everything after self.curindex+1 is beyond the top of the
        # stack. this seems to be relevant only when there's an exception,
        # since the ENTIRE stack is preserved but self.curindex
        # starts decrementing as the exception bubbles up the stack.
        cur_stack_frames = [e[0] for e in self.stack[:self.curindex+1]]
        zombie_frames_to_render = [e for e in self.zombie_frames if e not in cur_stack_frames]


        # each element is a pair of (function name, ENCODED locals dict)
        encoded_stack_locals = []
        self.user_locals = dict()

        # returns a dict with keys: function name, frame id, id of parent frame, encoded_vars dict
        def create_encoded_stack_entry(cur_frame):
            #print >> sys.stderr, '- create_encoded_stack_entry', cur_frame, self.closures, self.lambda_closures
            ret = {}


            parent_frame_id_list = []

            f = cur_frame
            while True:
                p = self.get_parent_frame(f)
                if p:
                    pid = self.get_frame_id(p)
                    assert pid
                    parent_frame_id_list.append(pid)
                    f = p
                else:
                    break


            cur_name = cur_frame.f_code.co_name

            if cur_name == '':
                cur_name = 'unnamed function'

            # augment lambdas with line number
            if cur_name == '<lambda>':
                cur_name += pg_encoder.create_lambda_line_number(cur_frame.f_code,
                                                                 self.encoder.line_to_lambda_code)

            # encode in a JSON-friendly format now, in order to prevent ill
            # effects of aliasing later down the line ...
            encoded_vars = {}

            user_locals = get_user_locals(cur_frame)
            self.user_locals.update(copy.deepcopy(user_locals))
            for (k, v) in user_locals.items():
                is_in_parent_frame = False

                # don't display locals that appear in your parents' stack frames,
                # since that's redundant
                for pid in parent_frame_id_list:
                    parent_frame = self.lookup_zombie_frame_by_id(pid)
                    if k in parent_frame.f_locals:
                    # ignore __return__, which is never copied
                        if k != '__return__':
                            # these values SHOULD BE ALIASES
                            # (don't do an 'is' check since it might not fire for primitives)
                            if parent_frame.f_locals[k] == v:
                                is_in_parent_frame = True

                if is_in_parent_frame and k not in cur_frame.f_code.co_varnames:
                    continue

                # don't display some built-in locals ...
                if k == '__module__':
                    continue

                if self.should_hide_var(k):
                    continue

                encoded_val = self.encoder.encode(v, self.get_parent_of_function)
                encoded_vars[k] = encoded_val


            # order the variable names in a sensible way:

            # Let's start with co_varnames, since it (often) contains all
            # variables in this frame, some of which might not exist yet.
            ordered_varnames = []
            for e in cur_frame.f_code.co_varnames:
                if e in encoded_vars:
                    ordered_varnames.append(e)

            # sometimes co_varnames doesn't contain all of the true local
            # variables: e.g., when executing a 'class' definition.  in that
            # case, iterate over encoded_vars and push them onto the end
            # of ordered_varnames in alphabetical order
            for e in sorted(encoded_vars.keys()):
                if e != '__return__' and e not in ordered_varnames:
                    ordered_varnames.append(e)

            # finally, put __return__ at the very end
            if '__return__' in encoded_vars:
                ordered_varnames.append('__return__')

            # doctor Python 3 initializer to look like a normal function (denero)
            if '__locals__' in encoded_vars:
                ordered_varnames.remove('__locals__')
                local = encoded_vars.pop('__locals__')
                if encoded_vars.get('__return__', True) is None:
                    encoded_vars['__return__'] = local

            # crucial sanity checks!
            assert len(ordered_varnames) == len(encoded_vars)
            for e in ordered_varnames:
                assert e in encoded_vars

            return dict(func_name=cur_name,
                        is_parent=(cur_frame in self.parent_frames_set),
                        frame_id=self.get_frame_id(cur_frame),
                        parent_frame_id_list=parent_frame_id_list,
                        encoded_vars=encoded_vars,
                        ordered_varnames=ordered_varnames,
                        prev_encoded_vars=dict())


        i = self.curindex

        # look for whether a nested function has been defined during
        # this particular call:
        if i > 1: # i == 1 implies that there's only a global scope visible
            for v in visit_all_locally_reachable_function_objs(top_frame):
                if (v not in self.closures and \
                    v not in self.globally_defined_funcs):

                    # Look for the presence of the code object (v.func_code
                    # for Python 2 or v.__code__ for Python 3) in the
                    # constant pool (f_code.co_consts) of an enclosing
                    # stack frame, and set that frame as your parent.
                    #
                    # This technique properly handles lambdas passed as
                    # function parameters. e.g., this example:
                    #
                    # def foo(x):
                    #   bar(lambda y: x + y)
                    # def bar(a):
                    #   print a(20)
                    # foo(10)
                    chosen_parent_frame = None
                    # SUPER hacky but seems to work -- use reversed(self.stack)
                    # because we want to traverse starting from the TOP of the stack
                    # (most recent frame) and find the first frame containing
                    # a constant code object that matches v.__code__ or v.func_code
                    #
                    # required for this example from Berkeley CS61a:
                    #
                    # def f(p, k):
                    #     def g():
                    #         print(k)
                    #     if k == 0:
                    #         f(g, 1)
                    # f(None, 0)
                    #
                    # there are two calls to f, each of which defines a
                    # closure g that should point to the respective frame.
                    #
                    # note that for the second call to f, the parent of the
                    # g defined in there should be that frame, which is at
                    # the TOP of the stack. this reversed() hack does the
                    # right thing. note that if you don't traverse the stack
                    # backwards, then you will mistakenly get the parent as
                    # the FIRST f frame (bottom of the stack).
                    for (my_frame, my_lineno) in reversed(self.stack):
                        if chosen_parent_frame:
                            break

                        for frame_const in my_frame.f_code.co_consts:
                            if frame_const is (v.__code__ if is_python3 else v.func_code):
                                chosen_parent_frame = my_frame
                                break

                    # 2013-12-01 commented out this line so tests/backend-tests/papajohn-monster.txt
                    # works without an assertion failure ...
                    #assert chosen_parent_frame # I hope this always passes :0

                    # this condition should be False for functions declared in global scope ...
                    if chosen_parent_frame in self.frame_ordered_ids:
                        self.closures[v] = chosen_parent_frame
                        self.parent_frames_set.add(chosen_parent_frame) # unequivocally add to this set!!!
                        if not chosen_parent_frame in self.zombie_frames:
                            self.zombie_frames.append(chosen_parent_frame)
            else:
                # look for code objects of lambdas defined within this
                # function, which comes up in cases like line 2 of:
                # def x(y):
                #   (lambda z: lambda w: z+y)(y)
                #
                # x(42)
                if top_frame.f_code.co_consts:
                    for e in top_frame.f_code.co_consts:
                        if type(e) == types.CodeType and e.co_name == '<lambda>':
                            # TODO: what if it's already in lambda_closures?
                            self.lambda_closures[e] = top_frame
                            self.parent_frames_set.add(top_frame) # copy-paste from above
                            if not top_frame in self.zombie_frames:
                                self.zombie_frames.append(top_frame)
        else:
            # if there is only a global scope visible ...
            for (k, v) in get_user_globals(top_frame).items():
                if (type(v) in (types.FunctionType, types.MethodType) and \
                    v not in self.closures):
                    self.globally_defined_funcs.add(v)


        # climb up until you find '<module>', which is (hopefully) the global scope
        top_frame = None
        while True:
            cur_frame = self.stack[i][0]
            cur_name = cur_frame.f_code.co_name
            if cur_name == '<module>':
                break

            # do this check because in some cases, certain frames on the
            # stack might NOT be tracked, so don't push a stack entry for
            # those frames. this happens when you have a callback function
            # in an imported module. e.g., your code:
            #     def foo():
            #         bar(baz)
            #
            #     def baz(): pass
            #
            # imported module code:
            #     def bar(callback_func):
            #         callback_func()
            #
            # when baz is executing, the real stack is [foo, bar, baz] but
            # bar is in imported module code, so pg_logger doesn't trace
            # it, and it doesn't show up in frame_ordered_ids. thus, the
            # stack to render should only be [foo, baz].
            if cur_frame in self.frame_ordered_ids:
                encoded_stack_locals.append(create_encoded_stack_entry(cur_frame))
                if not top_frame:
                    top_frame = cur_frame
            i -= 1

        zombie_encoded_stack_locals = [create_encoded_stack_entry(e) for e in zombie_frames_to_render]


        # encode in a JSON-friendly format now, in order to prevent ill
        # effects of aliasing later down the line ...
        encoded_globals = {}
        cur_globals_dict = get_user_globals(tos[0], at_global_scope=(self.curindex <= 1))
        self.user_globals = copy.deepcopy(cur_globals_dict)
        for (k, v) in cur_globals_dict.items():
            if self.should_hide_var(k):
                continue

            encoded_val = self.encoder.encode(v, self.get_parent_of_function)
            encoded_globals[k] = encoded_val

            if k not in self.all_globals_in_order:
                self.all_globals_in_order.append(k)

        # filter out globals that don't exist at this execution point
        # (because they've been, say, deleted with 'del')
        ordered_globals = [e for e in self.all_globals_in_order if e in encoded_globals]
        assert len(ordered_globals) == len(encoded_globals)


        # merge zombie_encoded_stack_locals and encoded_stack_locals
        # into one master ordered list using some simple rules for
        # making it look aesthetically pretty
        stack_to_render = []

        # first push all regular stack entries
        if encoded_stack_locals:
            for e in encoded_stack_locals:
                e['is_zombie'] = False
                e['is_highlighted'] = False
                stack_to_render.append(e)

            # highlight the top-most active stack entry
            stack_to_render[0]['is_highlighted'] = True


        # now push all zombie stack entries
        for e in zombie_encoded_stack_locals:
            # don't display return value for zombie frames
            # TODO: reconsider ...
            '''
            try:
              e['ordered_varnames'].remove('__return__')
            except ValueError:
              pass
            '''

            e['is_zombie'] = True
            e['is_highlighted'] = False # never highlight zombie entries

            stack_to_render.append(e)

        # now sort by frame_id since that sorts frames in "chronological
        # order" based on the order they were invoked
        stack_to_render.sort(key=lambda e: e['frame_id'])



        # create a unique hash for this stack entry, so that the
        # frontend can uniquely identify it when doing incremental
        # rendering. the strategy is to use a frankenstein-like mix of the
        # relevant fields to properly disambiguate closures and recursive
        # calls to the same function
        for e in stack_to_render:
            hash_str = 'call'
            # frame_id is UNIQUE, so it can disambiguate recursive calls
            hash_str += '_f' + str(e['frame_id'])

            # needed to refresh GUI display ...
            if e['is_parent']:
                hash_str += '_p'

            # TODO: this is no longer needed, right? (since frame_id is unique)
            #if e['parent_frame_id_list']:
            #  hash_str += '_p' + '_'.join([str(i) for i in e['parent_frame_id_list']])
            if e['is_zombie']:
                hash_str += '_z'

            e['unique_hash'] = hash_str
            e['prev_encoded_vars'] = dict()


        # handle probe_exprs *before* encoding the heap with self.encoder.get_heap
        encoded_probe_vals = {}
        if self.probe_exprs:
            if top_frame: # are we in a function call?
                top_frame_locals = get_user_locals(top_frame)
            else:
                top_frame_locals = {}
            for e in self.probe_exprs:
                try:
                                # evaluate it with globals + locals of the top frame ...
                    probe_val = eval(e, cur_globals_dict, top_frame_locals)
                    encoded_probe_vals[e] = self.encoder.encode(probe_val, self.get_parent_of_function)
                except:
                    pass # don't encode the value if there's been an error

            
        # Agrega información de en qué pasó se imprimió y si fue dentro de un ciclo
        stdout = self.get_user_stdout()
        if self.prev_lineno > 0 and self.executed_script_lines[self.prev_lineno - 1].strip().startswith('print'):
            if stdout.endswith('\n'):
                stdout = stdout[:-1]
            
            trace_len = len(self.trace) + 1
            stdout += '&emsp;<i style="color: gray"> ... Paso: ' + str(trace_len)

            if self.registered_loops['stack']:
                current = self.registered_loops['stack'][-1]
                curr_loop = self.registered_loops[current]
                loop_type = curr_loop['type']
                stdout += ''' | </i><i style="color: #{0}">Ciclo: {1} </i><i style="color:gray">({2} línea {3})'''.format('FFCA28' if loop_type == 'for' else '4CAF50', curr_loop['current'] + 1, loop_type, curr_loop['line'])
            stdout += '</i>\n'

        global_scope = dict(encoded_vars=encoded_globals,
                            ordered_varnames=ordered_globals,
                            prev_encoded_vars=dict())

        # Para ver cambios en valores de variables
        recursion_overflow = False
        if self.trace:
            prev_stack_format = copy.deepcopy(self.trace[-1]['stack_to_render'])

            # Ver cambios en el scope global
            prev_global = prev_stack_format['global']
            prev_stack_format['global'] = self.check_variable_value_changes(prev_global, global_scope)

            # Buscar cambios en scopes locales
            last_scope_name = prev_stack_format['ordered_scopes'][-1]
            if stack_to_render:
                current_scope = stack_to_render[-1]
                current_scope_name = current_scope['func_name']
                current_hash = current_scope['unique_hash']
                if current_scope_name in prev_stack_format:
                    last_scope_name = prev_stack_format['ordered_scopes'][-1]
                    if not current_scope_name == last_scope_name:
                        del prev_stack_format[last_scope_name]
                        prev_stack_format['ordered_scopes'] = prev_stack_format['ordered_scopes'][:-1]

                    scope = prev_stack_format[current_scope_name]
                    last_hash = scope['ordered_hashes'][-1]
                    if not current_hash in scope['ordered_hashes']:
                        scope[current_hash] = current_scope
                        scope['ordered_hashes'].append(current_hash)
                        if len(scope) > MAX_RECURSIVE_CALLS:
                            recursion_overflow = True
                    elif current_hash == last_hash:
                        if '__return__' in current_scope['ordered_varnames']:
                            current_scope['returned'] = current_scope['encoded_vars']['__return__']
                            del current_scope['encoded_vars']['__return__']
                            current_scope['ordered_varnames'].pop()
                        scope[last_hash] = self.check_variable_value_changes(scope[last_hash], current_scope)
                    else:
                        del scope[last_hash]
                        scope['ordered_hashes'].pop()
                        scope[current_hash] = self.check_variable_value_changes(scope[current_hash], current_scope)
                else:
                    scope = { current_hash: current_scope, 'ordered_hashes': [current_hash] }
                    prev_stack_format['ordered_scopes'] = prev_stack_format['ordered_scopes'] + [current_scope_name]

                del current_scope['unique_hash']
                del current_scope['func_name']
                prev_stack_format[current_scope_name] = scope
            elif not last_scope_name == 'global':
                del prev_stack_format[last_scope_name]
                prev_stack_format['ordered_scopes'].pop()
        else:
            prev_stack_format = { 'global' : global_scope, 'ordered_scopes': ['global'] }

        if self.show_only_outputs:
            trace_entry = dict(line=self.lineno,
                               event=event_type,
                               func_name=tos[0].f_code.co_name,
                               stack_to_render=[],
                               stdout=stdout)
        else:
            trace_entry = dict(line=self.lineno,
                               event=event_type,
                               func_name=tos[0].f_code.co_name,
                               stack_to_render=prev_stack_format,
                               stdout=stdout)
            if encoded_probe_vals:
                trace_entry['probe_exprs'] = encoded_probe_vals
                
        line = self.executed_script_lines[self.lineno - 1].strip()
        ins_type = 'loop' if line.startswith(('for', 'while')) else \
                   'conditional' if line.startswith(('if', 'elif')) else ''

        self.current_stack = prev_stack_format

        loop = None
        cond = None
        if ins_type == 'loop':
            # Registra y actualiza loops (while y for)
            if self.lineno in self.registered_loops:
                loop = self.update_loop()
            else:
                loop = self.register_loop(line)
            trace_entry.update(dict(loop=loop))
        elif ins_type == 'conditional':
            cond = self.trace_conditional(line)
            trace_entry.update(dict(conditional=cond))

        # optional column numbers for greater precision
        # (only relevant in Py2crazy, a hacked CPython that supports column numbers)
        if self.crazy_mode:
            # at the very least, grab the column number
            trace_entry['column'] = frame.f_colno

            # now try to find start_col and extent
            # (-1 is an invalid instruction index)
            if frame.f_lasti >= 0:
                key = (frame.f_code.co_code, frame.f_lineno, frame.f_colno,frame.f_lasti)
                if key in self.bytecode_map:
                    v = self.bytecode_map[key]
                    trace_entry['expr_start_col'] = v.start_col
                    trace_entry['expr_width'] = v.extent
                    trace_entry['opcode'] = v.opcode

        # set a 'custom_module_name' field if we're executing in a module
        # that's not the __main__ script:
        if topframe_module != "__main__":
            trace_entry['custom_module_name'] = topframe_module

        # if there's an exception, then record its info:
        if event_type == 'exception':
            # always check in f_locals
            exc = frame.f_locals['__exception__']
            trace_entry['exception_msg'] = exc[0].__name__ + ': ' + str(exc[1])


        # append to the trace only the breakpoint line and the next
        # executed line, so that if you set only ONE breakpoint, OPT shows
        # the state before and after that line gets executed.
        append_to_trace = True
        if self.breakpoints:
            if not ((self.lineno in self.breakpoints) or (self.prev_lineno in self.breakpoints)):
                append_to_trace = False

            # TRICKY -- however, if there's an exception, then ALWAYS
            # append it to the trace, so that the error can be displayed
            if event_type == 'exception':
                append_to_trace = True

        self.prev_lineno = self.lineno

        if append_to_trace:
            self.trace.append(trace_entry)

        line_limit_reached = len(self.trace) >= MAX_EXECUTED_LINES
        if line_limit_reached or recursion_overflow:
            message = MAX_RECURSIVE_CALLS_REACHED.format(current_scope_name, MAX_RECURSIVE_CALLS) if recursion_overflow else MAX_EXECUTED_LINES_REACHED.format(MAX_EXECUTED_LINES)
            self.trace.append(dict(event='instruction_limit_reached',
                                   line=self.lineno,
                                   exception_msg=message,
                                   limit='steps'))
            self.force_terminate()

        self.forget()

    def _runscript(self, script_str):
        self.executed_script = script_str
        self.executed_script_lines = self.executed_script.splitlines()

        for (i, line) in enumerate(self.executed_script_lines):
            line_no = i + 1
            # subtle -- if the stripped line starts with '#break', that
            # means it may be a commented-out version of a normal Python
            # 'break' statement, which shouldn't be confused with an
            # OPT user-defined breakpoint!
            #
            # TODO: this still fails when someone writes something like
            # '##break' since it doesn't start with '#break'!!! i just
            # picked an unfortunate name that's also a python keyword :0
            if line.endswith(BREAKPOINT_STR) and not line.strip().startswith(BREAKPOINT_STR):
                self.breakpoints.append(line_no)

            if line.startswith(PYTUTOR_HIDE_STR):
                hide_vars = line[len(PYTUTOR_HIDE_STR):]
                # remember to call strip() -> compileGlobMatch()
                hide_vars = [compileGlobMatch(e.strip()) for e in hide_vars.split(',')]
                self.vars_to_hide.update(hide_vars)

            if line.startswith(PYTUTOR_INLINE_TYPE_STR):
                listed_types = line[len(PYTUTOR_INLINE_TYPE_STR):]
                # remember to call strip() -> compileGlobMatch()
                listed_types = [compileGlobMatch(e.strip()) for e in listed_types.split(',')]
                self.types_to_inline.update(listed_types)

        # populate an extent map to get more accurate ranges from code
        if self.crazy_mode:
            # in Py2crazy standard library as Python-2.7.5/Lib/super_dis.py
            import super_dis
            try:
                self.bytecode_map = super_dis.get_bytecode_map(self.executed_script)
            except:
                # failure oblivious
                self.bytecode_map = {}

        # When bdb sets tracing, a number of call and line events happens
        # BEFORE debugger even reaches user's code (and the exact sequence of
        # events depends on python version). So we take special measures to
        # avoid stopping before we reach the main script (see user_line and
        # user_call for details).
        self._wait_for_mainpyfile = 1


        # ok, let's try to sorta 'sandbox' the user script by not
        # allowing certain potentially dangerous operations.
        user_builtins = {}

        # ugh, I can't figure out why in Python 2, __builtins__ seems to
        # be a dict, but in Python 3, __builtins__ seems to be a module,
        # so just handle both cases ... UGLY!
        if type(__builtins__) is dict:
            builtin_items = __builtins__.items()
        else:
            assert type(__builtins__) is types.ModuleType
            builtin_items = []
            for k in dir(__builtins__):
                builtin_items.append((k, getattr(__builtins__, k)))

        for (k, v) in builtin_items:
            if k == 'open' and not self.allow_all_modules: # put this before BANNED_BUILTINS
                user_builtins[k] = open_wrapper
            elif k in BANNED_BUILTINS:
                user_builtins[k] = create_banned_builtins_wrapper(k)
            elif k == '__import__' and not self.allow_all_modules:
                user_builtins[k] = __restricted_import__
            else:
                if k == 'raw_input':
                    user_builtins[k] = raw_input_wrapper
                elif k == 'input':
                    if is_python3:
                # Python 3 input() is Python 2 raw_input()
                        user_builtins[k] = raw_input_wrapper
                    else:
                        user_builtins[k] = python2_input_wrapper
                else:
                    user_builtins[k] = v

        user_builtins['mouse_input'] = mouse_input_wrapper

        if self.separate_stdout_by_module:
            self.stdout_by_module["__main__"] = StringIO.StringIO()
            if self.custom_modules:
                for module_name in self.custom_modules:
                    self.stdout_by_module[module_name] = StringIO.StringIO()
            self.stdout_by_module["<other>"] = StringIO.StringIO() # catch-all for all other modules we're NOT tracing
            sys.stdout = self.stdout_by_module["<other>"] # start with <other>
        else:
            # default -- a single unified stdout stream
            self.user_stdout = StringIO.StringIO()
            sys.stdout = self.user_stdout

        # don't do this, or else certain kinds of errors, such as syntax
        # errors, will be silently ignored. WEIRD!
        #sys.stderr = NullDevice # silence errors

        user_globals = {}

        # if there are custom_modules, 'import' them into user_globals,
        # which emulates "from <module> import *"
        if self.custom_modules:
            for mn in self.custom_modules:
                        # http://code.activestate.com/recipes/82234-importing-a-dynamically-generated-module/
                new_m = imp.new_module(mn)
                exec(self.custom_modules[mn], new_m.__dict__) # exec in custom globals
                user_globals.update(new_m.__dict__)

        # important: do this LAST to get precedence over values in custom_modules
        user_globals.update({"__name__"    : "__main__",
                             "__builtins__" : user_builtins})

        try:
            # if allow_all_modules is on, then try to parse script_str into an
            # AST, traverse the tree to find all modules that it imports, and then
            # try to PRE-IMPORT all of those. if we *don't* pre-import a module,
            # then when it's imported in the user's code, it may take *forever*
            # because the bdb debugger tries to single-step thru that code
            # (i think!). run 'import pandas' to quickly test this.
            if self.allow_all_modules:
                import ast
                try:
                    all_modules_to_preimport = []
                    tree = ast.parse(script_str)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for n in node.names:
                                all_modules_to_preimport.append(n.name)
                        elif isinstance(node, ast.ImportFrom):
                            all_modules_to_preimport.append(node.module)

                    for m in all_modules_to_preimport:
                        if m in script_str: # optimization: load only modules that appear in script_str
                            try:
                                __import__(m)
                            except ImportError:
                                pass
                except:
                    pass


            # enforce resource limits RIGHT BEFORE running script_str

            # set ~200MB virtual memory limit AND a 5-second CPU time
            # limit (tuned for Webfaction shared hosting) to protect against
            # memory bombs such as:
            #   x = 2
            #   while True: x = x*x
            if resource_module_loaded and (not self.disable_security_checks):
                assert not self.allow_all_modules # <-- shouldn't be on!

                # PREEMPTIVELY import all of these modules, so that when the user's
                # script imports them, it won't try to do a file read (since they've
                # already been imported and cached in memory). Remember that when
                # the user's code runs, resource.setrlimit(resource.RLIMIT_NOFILE, (0, 0))
                # will already be in effect, so no more files can be opened.
                for m in ALLOWED_STDLIB_MODULE_IMPORTS:
                    if m in script_str: # optimization: load only modules that appear in script_str
                        try:
                            __import__(m)
                        except ImportError:
                            pass

                resource.setrlimit(resource.RLIMIT_AS, (200000000, 200000000))
                resource.setrlimit(resource.RLIMIT_CPU, (5, 5))

                # protect against unauthorized filesystem accesses ...
                resource.setrlimit(resource.RLIMIT_NOFILE, (0, 0)) # no opened files allowed

                # VERY WEIRD. If you activate this resource limitation, it
                # ends up generating an EMPTY trace for the following program:
                #   "x = 0\nfor i in range(10):\n  x += 1\n   print x\n  x += 1\n"
                # (at least on my Webfaction hosting with Python 2.7)
                #resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))  # (redundancy for paranoia)

                # The posix module is a built-in and has a ton of OS access
                # facilities ... if you delete those functions from
                # sys.modules['posix'], it seems like they're gone EVEN IF
                # someone else imports posix in a roundabout way. Of course,
                # I don't know how foolproof this scheme is, though.
                # (It's not sufficient to just "del sys.modules['posix']";
                #  it can just be reimported without accessing an external
                #  file and tripping RLIMIT_NOFILE, since the posix module
                #  is baked into the python executable, ergh. Actually DON'T
                #  "del sys.modules['posix']", since re-importing it will
                #  refresh all of the attributes. ergh^2)
                for a in dir(sys.modules['posix']):
                    delattr(sys.modules['posix'], a)
                # do the same with os
                for a in dir(sys.modules['os']):
                    # 'path' is needed for __restricted_import__ to work
                    # and 'stat' is needed for some errors to be reported properly
                    if a not in ('path', 'stat'):
                        delattr(sys.modules['os'], a)
                # ppl can dig up trashed objects with gc.get_objects()
                import gc
                for a in dir(sys.modules['gc']):
                    delattr(sys.modules['gc'], a)
                del sys.modules['gc']

                # sys.modules contains an in-memory cache of already-loaded
                # modules, so if you delete modules from here, they will
                # need to be re-loaded from the filesystem.
                #
                # Thus, as an extra precaution, remove these modules so that
                # they can't be re-imported without opening a new file,
                # which is disallowed by resource.RLIMIT_NOFILE
                #
                # Of course, this isn't a foolproof solution by any means,
                # and it might lead to UNEXPECTED FAILURES later in execution.
                del sys.modules['os']
                del sys.modules['os.path']
                del sys.modules['sys']

            self.user_globals = user_globals
            self.run(script_str, user_globals, user_globals)
        # sys.exit ...
        except SystemExit:
            #sys.exit(0)
            raise bdb.BdbQuit
        except:
            if DEBUG:
                traceback.print_exc()

            trace_entry = dict(event='uncaught_exception')

            (exc_type, exc_val, exc_tb) = sys.exc_info()
            trace_entry['line'] = self.lineno
            if hasattr(exc_val, 'offset'):
                trace_entry['offset'] = exc_val.offset

            trace_entry['exception_msg'] = type(exc_val).__name__ + ": " +  str(exc_val)

            # SUPER SUBTLE! if ANY exception has already been recorded by
            # the program, then DON'T record it again as an uncaught_exception.
            # This looks kinda weird since the exact exception message doesn't
            # need to match up, but in practice, there should be at most only
            # ONE exception per trace.
            already_caught = False
            for e in self.trace:
                if e['event'] == 'exception':
                    already_caught = True
                    break

            if not already_caught:
                if not self.done:
                    self.trace.append(trace_entry)

            raise bdb.BdbQuit # need to forceably STOP execution


    def force_terminate(self):
        #self.finalize()
        raise bdb.BdbQuit # need to forceably STOP execution


    def finalize(self):
        sys.stdout = self.GAE_STDOUT # very important!
        sys.stderr = self.ORIGINAL_STDERR
        assert len(self.trace) <= (MAX_EXECUTED_LINES + 1)

        res = self.trace

        # if the SECOND to last entry is an 'exception'
        # and the last entry is return from <module>, then axe the last
        # entry, for aesthetic reasons :)
        if len(res) >= 2 and \
           res[-2]['event'] == 'exception' and \
           res[-1]['event'] == 'return' and res[-1]['func_name'] == '<module>':
            res.pop()

        return self.trace

import json

# the MAIN meaty function!!!
def exec_script_str(script_str, raw_input_lst_json, options_json):
    if options_json:
        options = json.loads(options_json)
    else:
        # defaults
        options = {'cumulative_mode': False,
                   'heap_primitives': False, 'show_only_outputs': False}

    py_crazy_mode = ('py_crazy_mode' in options and options['py_crazy_mode'])

    logger = PGLogger(options['cumulative_mode'], options['heap_primitives'], options['show_only_outputs'],
                      crazy_mode=py_crazy_mode)

    # TODO: refactor these NOT to be globals
    global input_string_queue
    input_string_queue = []
    if raw_input_lst_json:
        # TODO: if we want to support unicode, remove str() cast
        input_string_queue = [str(e) for e in json.loads(raw_input_lst_json)]

    try:
        logger._runscript(script_str)
    except bdb.BdbQuit:
        pass
    finally:
        logger.finalize()

# WARNING: ONLY RUN THIS LOCALLY and never over the web, since
# security checks are disabled
#
# [optional] probe_exprs is a list of strings representing
# expressions whose values to probe at each step (advanced)
def exec_script_str_local(script_str, raw_input_lst_json, cumulative_mode, heap_primitives,
                          probe_exprs=None, allow_all_modules=False):
    logger = PGLogger(cumulative_mode, heap_primitives, False,
                      disable_security_checks=True,
                      allow_all_modules=allow_all_modules,
                      probe_exprs=probe_exprs)

    # TODO: refactor these NOT to be globals
    global input_string_queue
    input_string_queue = []
    if raw_input_lst_json:
        # TODO: if we want to support unicode, remove str() cast
        input_string_queue = [str(e) for e in raw_input_lst_json]

    try:
        logger._runscript(script_str)
    except bdb.BdbQuit:
        pass
    finally:
        return logger.finalize()
