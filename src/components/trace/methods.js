import VarTypes from '@/vartypes'

export default {
    color: function(depth = 0) {
        const base = 80 + depth * 25
        return 'rgb(' + base + ', ' + base + ', ' + (base + 10) + ')'
    },
    decode: function(value, vartype = undefined) {
        const type = vartype || this.type(value)
        if(type === VarTypes.DICT || type.includes(VarTypes.LIST) || type === VarTypes.MATRIX) {
            return value.slice(1)
        } else if(type === VarTypes.FUNCTION) {
            const func = value[1].replace('(', ',').replace(')', '').replace(/\s/g, '').split(',')
            return { name: func[0], params: func.slice(1) }
        } else if(type === VarTypes.STRING) {
            return value.replace(/\b\n\b/g, '<br>')
        } else if(type === VarTypes.NUMBER || type === VarTypes.FLOAT) {
            value = value[1] || value
            const parts = value.toString().split('.')
            const number = parts[0]
            const base = number.length % 3 || 3
            const steps = Math.floor(number.length / 3) + (base === 3 ? 0 : 1)
            let formatted = number.substr(0, base)
            for(let i = 1; i < steps; i ++)
                formatted += '.' + number.substr(i * base, 3)
            return parts.length === 2 ? formatted + ',' + parts[1] : formatted
        }
        return value
    },
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
    value: function(variable, vartype = undefined) {
        const type = vartype || this.type(variable)
        switch(type) {
            case VarTypes.BOOLEAN: return variable ? 'True': 'False'
            case VarTypes.DICT: return '{ }'
            case VarTypes.FLOAT: return variable[1] || variable
            case VarTypes.FUNCTION: return 'fx()'
            case VarTypes.LIST: return '[ ]'
            case VarTypes.LIST_OF_LISTS: return '<i class="md-icon md-icon-font md-theme-secondary">format_list_bulleted</i>'
            case VarTypes.MATRIX: return '<i class="md-icon md-icon-font md-theme-secondary">apps</i>'
            default: return variable
        }
    }
}