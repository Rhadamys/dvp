import VarTypes from '@/vartypes'

export default {
    color: function(depth = 0) {
        const base = 80 + depth * 25
        return 'rgb(' + base + ', ' + base + ', ' + (base + 10) + ')'
    },
    decode: function(value) {
        const type = this.type(value)
        if(type === VarTypes.DICT || type.includes(VarTypes.LIST) || type === VarTypes.MATRIX)
            return value.slice(1)
        else if(type === VarTypes.FUNCTION) {
            const func = value[1].replace('(', ',').replace(')', '').replace(/\s/g, '').split(',')
            return { name: func[0], params: func.slice(1) }
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
        return (type === 'string' && variable.includes('.') && !isNaN(variable)) ? 'number' : type
    },
    value: function(variable) {
        const type = this.type(variable)
        switch(type) {
            case VarTypes.BOOLEAN: return variable ? 'True': 'False'
            case VarTypes.DICT: return '{ }'
            case VarTypes.FLOAT: return variable[1]
            case VarTypes.FUNCTION: return 'fx()'
            case VarTypes.LIST: return '[ ]'
            case VarTypes.LIST_OF_LISTS: return '<i class="md-icon md-icon-font md-theme-secondary">format_list_bulleted</i>'
            case VarTypes.MATRIX: return '<i class="md-icon md-icon-font md-theme-secondary">apps</i>'
            default: return variable
        }
    }
}