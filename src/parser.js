import Annotations from '@/annotations'
import Events from '@/events'
import VarTypes from '@/vartypes'

const VARIABLE_SCALE_COLORS = {
    boolean: '#9c27b0',
    char: ['#ffca28','#ffc124','#ffb720','#ffaf1c','#ffa417','#ff9a13','#ff910e','#ff8609','#ff7b04','#ff6f00'],
    dict: ['#5c6bc0','#5562b8','#4f5ab1','#4852aa','#424aa2','#3b429b','#333a94','#2c338c','#232a85','#1a237e'],
    float: ['#42a5f5','#3e9aec','#398fe2','#3485d8','#2f79cf','#2a70c6','#2465bd','#1e5ab3','#1651aa','#0d47a1'],
    function: '#795548',
    list: ['#66bb6a','#5eb162','#55a559','#4d9a50','#459048','#3c8640','#347b37','#2c7230','#236728','#1b5e20'],
    listoflists: ['#66bb6a','#5eb162','#55a559','#4d9a50','#459048','#3c8640','#347b37','#2c7230','#236728','#1b5e20'],
    matrix: ['#66bb6a','#5eb162','#55a559','#4d9a50','#459048','#3c8640','#347b37','#2c7230','#236728','#1b5e20'],
    number: ['#42a5f5','#3e9aec','#398fe2','#3485d8','#2f79cf','#2a70c6','#2465bd','#1e5ab3','#1651aa','#0d47a1'],
    object: '#bdbdbd',
    string: ['#ffca28','#ffc124','#ffb720','#ffaf1c','#ffa417','#ff9a13','#ff910e','#ff8609','#ff7b04','#ff6f00'],
}

export default {
    /**
     * Determina el color que debe tener una caja de variable.
     * @param scale Escala de valores por tipo de dato.
     * @param type Tipo de dato de la variable que se evalúa.
     * @param factor Factor de la variable dentro de la escala actual.
     * @returns Cógido hexadecimal del color que tendrá la caja.
     */
    color: function(scale, type, factor) {
        if(type === VarTypes.BOOLEAN || type === VarTypes.FUNCTION || type === VarTypes.OBJECT)
            return VARIABLE_SCALE_COLORS[type]

        const min = scale[type]['min']
        const current = factor - min
        const upper = scale[type]['max'] - min
        if(upper === 0)
            return VARIABLE_SCALE_COLORS[type][4]
        
        const index = Math.floor(current * 9 / upper)
        return VARIABLE_SCALE_COLORS[type][index]
    },
    /**
     * Determina el factor de una variable. El factor es como el peso que tiene el valor
     * de la variable. Utilizado para la escala por tipos de dato.
     * @param variable Variable que se evaluará.
     * @returns Factor de la variable evaluada. 
     */
    factor: function(variable) {
        switch(variable.type) {
            case VarTypes.CHAR: return variable.value.charCodeAt(0)
            case VarTypes.DICT: {
                let len = 0
                for(let key in variable.value) {
                    const val = variable.value[key]
                    len += this.factor(val)
                }
                return len
            }
            case VarTypes.LIST:
            case VarTypes.STRING:
                return variable.value.length
            case VarTypes.LIST_OF_LISTS:
            case VarTypes.MATRIX: {
                let len = 0
                variable.value.forEach(row => {
                    row.value.forEach(element => {
                        len += this.factor(element)
                    })
                })
                return len
            }
            case VarTypes.NUMBER:
            case VarTypes.FLOAT:
                return variable.value
            default: return 1
        }
    },
    /**
     * Formato alternativo para valores numéricos. Por ejemplo, los decimales aparecerán
     * con comas y puntos utilizando la notación nacional en lugar de la americana.
     * @param value Valor numérico que se dará formato.
     * @return Valor formateado.
     */
    formatNumber: function(value) {
        value = value.toString()
        if(!value.includes('.')) return undefined
        
        const parts = value.split('.')
        const number = parts[0]
        const base = number.length % 3 || 3
        const steps = Math.floor(number.length / 3) + (base === 3 ? 0 : 1)
        let formatted = number.substr(0, base)
        for(let i = 1; i < steps; i ++)
            formatted += '.' + number.substr(i * base, 3)
        return parts.length === 2 ? formatted + ',' + parts[1] : formatted
    },
    /**
     * Indica el icono que debe mostrar una caja de variable de acuerdo a su tipo de dato.
     * @param type Tipo de dato la variable.
     * @return Icono en formato string para renderizar en el front.
     */
    icon: function(type) {
        switch(type) {
            case VarTypes.DICT: return '{ }'
            case VarTypes.FUNCTION: return 'fx()'
            case VarTypes.LIST: return '[ ]'
            case VarTypes.LIST_OF_LISTS: return '<i class="md-icon md-icon-font md-theme-secondary">format_list_bulleted</i>'
            case VarTypes.MATRIX: return '<i class="md-icon md-icon-font md-theme-secondary">apps</i>'
            default: return undefined
        }
    },
    /**
     * Esta función busca variables dentro de una subexpresión en una expresión condicional.
     * Se llama desde parseConditional.
     * @param bracket Subexpresión que se evaluará.
     */
    parseBracket: function(bracket) {
        bracket.forEach(part => {
            if(typeof part === 'object') {
                if(0 in part)
                    this.parsePart(part)
                else if(part.type === 'variable')
                    part.value = this.parseVariable({ value: part.value })
            }
            else if(Array.isArray(part))
                this.parseBracket(part)
        })
    },
    /**
     * Esta función busca variables dentro de una expresión condicional para darles el formato
     * correcto para mostrarlas en el front.
     * @param conditional Expresión condicional que se formaterá.
     * @returns Expresión condicional formateada.
     */
    parseConditional: function(conditional) {
        conditional.trace.forEach(step => {
            this.parseBracket(step.expression)
        })
        return conditional
    },
    /**
     * Esta función le da formato a una subexpresión como, por ejemplo, a == 2. Es el último
     * paso luego de llamar a parseConditional y parseBracket.
     * @param part Parte a la cual se evaluará si debe darse formato.
     */
    parsePart: function(part) {
        for(let key in part) {
            if(typeof part[key] === 'object') {
                if(0 in part[key])
                    this.parsePart(part[key])
                else if(part[key].type === 'variable')
                    part[key].value = this.parseVariable({ value: part[key].value })
            }
            else if(Array.isArray(part[key]))
                this.parseBracket(part[key])
        }
    },
    /**
     * Esta función le da formato a todas las variables dentro de una stack.
     * @param stack_to_render Stack al cual se le dará formato
     * @returns Stack con variables formateadas.
     */
    parseStack: function(stack_to_render) {
        const temp_stack = { order: [], scopes: {} }
        stack_to_render.ordered_scopes.forEach(scope_name => {
            const scope = stack_to_render[scope_name]
            let scope_entries = []
            if(scope_name === 'global') 
                scope_entries.push(scope)
            else {
                scope.ordered_hashes.forEach(hash => {
                    scope_entries.push(scope[hash])
                })
            }
            scope_entries.forEach(entry => {
                if('returned' in entry) {
                    const returned = this.parseVariable(entry['returned'])
                    const color = VARIABLE_SCALE_COLORS[returned.type]
                    returned['color'] = typeof color === 'string' ? color : color[4]
                    entry['returned'] = returned
                }

                entry.ordered_varnames.forEach(varname => {
                    const scale = {}
                    const current = this.parseVariable(entry.encoded_vars[varname])
                    const factor = this.scale(scale, current)
                    current['color'] = factor

                    if(varname in entry.prev_encoded_vars) {
                        entry.prev_encoded_vars[varname].forEach(prevalue => {
                            prevalue = this.parseVariable(prevalue)
                            prevalue['color'] = this.scale(scale, prevalue)
                        })
                    }

                    current.color = this.color(scale, current.type, factor)
                    if(varname in entry.prev_encoded_vars) {
                        entry.prev_encoded_vars[varname].forEach(prevalue => {
                            prevalue.color = this.color(scale, prevalue.type, prevalue.color)
                        })
                    }
                })
            })
            temp_stack.scopes[scope_name] = scope_entries
        })
        temp_stack.order = stack_to_render.ordered_scopes
        return temp_stack
    },
    /**
     * Esta función le da formato a las variables. Es el paso final de parseConditional
     * y parseStack. El formato consiste en agregar campos que son requeridos por el front,
     * y convertir el valor de otras propiedades.
     * @param variable Variable a la que se le dará formato.
     * @return Variable formateada.
     */
    parseVariable: function(variable) {
        let value = variable['value']
        const type = this.type(value)
        variable['type'] = type

        const icon = this.icon(type)
        if(icon) variable['icon'] = icon

        if(type === VarTypes.BOOLEAN) {
            variable['bool'] = value.toString()
            value = value ? 'True' : 'False'
        } else if(type === VarTypes.CHAR) {
            if(value === ' ') variable['parsed'] = 'Espacio (\\s)'
            else if(value === '\n') variable['parsed'] = 'Salto de línea (\\n)'
            else if(value === '\r') variable['parsed'] = 'Retorno de carro (\\r)'
            else if(value === '\t') variable['parsed'] = 'Marca de tabulación (\\t)'
        } else if(type === VarTypes.DICT) {
            const temp = {}
            for(let i = 1; i < value.length; i++) {
                const elmvar = { value: value[i][1] }
                const parsed = this.parseVariable(elmvar)
                temp[value[i][0]] = parsed
            }
            value = temp
        } else if(type === VarTypes.FLOAT || type === VarTypes.NUMBER) {
            value = Number(value[1] || value)
            variable['alternative'] = this.formatNumber(value)
        } else if(type === VarTypes.FUNCTION) {
            const params = value[1].replace('(', ',').replace(')', '').replace(/\s/g, '').split(',')
            const name = params.shift()
            value = { name, params }
        } else if(type.includes(VarTypes.LIST) || type === VarTypes.MATRIX) {
            const temp = []
            for(let i = 1; i < value.length; i++) {
                const elmvar = { value: value[i] }
                const parsed = this.parseVariable(elmvar)
                temp.push(parsed)
            }
            value = temp
        } else if(type === VarTypes.STRING) {
            const alternative = []
            for(let i = 0; i < value.length; i++) {
                const elmvar = { value: value[i] }
                const parsed = this.parseVariable(elmvar)
                alternative.push(parsed)
            }
            variable['alternative'] = alternative
            variable['parsed'] = value.replace(/\b\n\b/g, '<br>')
        }
        variable['value'] = value
        return variable
    },
    /**
     * Actualiza una escala de factores de acuerdo al tipo de dato de una
     * variable y al valor de la misma.
     * @param scale Escala de factores de variable.
     * @param variable Variable con la cual se actualizará la escala.
     * @return Escala de factores actualizada.
     */
    scale: function(scale, variable) {
        if(variable.type === VarTypes.BOOLEAN || 
            variable.type === VarTypes.FUNCTION || 
            variable.type === VarTypes.OBJECT)
            return null
        
        const factor = this.factor(variable)
        if(variable.type in scale) {
            if(factor < scale[variable.type]['min'])
                scale[variable.type]['min'] = factor
            if(factor > scale[variable.type]['max'])
                scale[variable.type]['max'] = factor
        } else {
            scale[variable.type] = { min: factor, max: factor }
        }
        return factor
    },
    /**
     * Transforma el tipo de dato indicado por el backend a un tipo de dato
     * válido para el frontend.
     * @param variable Variable para la cual se determinará el tipo de dato.
     * @return Tipo de dato, en formato string.
     */
    type: function(variable) {
        if(Array.isArray(variable)) {
            const ref_type = variable[0]
            switch(ref_type) {
                case 'DICT': return VarTypes.DICT
                case 'FUNCTION': return VarTypes.FUNCTION
                case 'LIST': return VarTypes.LIST
                case 'LIST_OF_LISTS': return VarTypes.LIST_OF_LISTS
                case 'MATRIX': return VarTypes.MATRIX
                case 'SPECIAL_FLOAT': return VarTypes.FLOAT
            }
        }
        
        const type = typeof variable
        if(type === 'number' && variable % 1 !== 0)
            return VarTypes.FLOAT
        else if(type === 'string' && variable.length === 1)
            return VarTypes.CHAR
        return type
    },
}