<template>
    <div class="timeline">
        <table>
            <div class="timeline-background">
                <div class="timeline-background-head"></div>
                <div class="timeline-background-body">
                    <div class="timeline-background-body-first" :class="{ 'timeline-returned' : scope.returned }"></div>
                    <div class="timeline-background-body-content"></div>
                </div>
            </div>
            <thead :id="'thead-' + id">
                <tr>
                    <th class="timeline-fixed-col">Variable</th>
                    <th v-for="i in range" :key="i" @click="$emit('step', i)" class="selectable">{{ i + 1 }}</th>
                </tr>
            </thead>
            <tbody :id="'tbody-' + id" @scroll="scroll">
                <tr v-if="'returned' in scope">
                    <td class="timeline-returned">
                        <div class="timeline-var-header">
                            <span>RETORNO</span>
                        </div>
                    </td>
                    <td class="timeline-variable timeline-returned-cell">
                        <div class="timeline-variable-value selectable md-elevation-4"
                            :class="scope.returned.bool" 
                            :style="'background-color: ' + scope.returned.color"
                            @mouseover="$emit('highlight', scope.returned.line)"
                            @mouseout="$emit('reset')"
                            @click="$emit('show', { varname: id, index: -1 })">
                            <span v-html="scope.returned.icon || scope.returned.value"></span>
                        </div>
                    </td>
                    <td v-for="i in range.slice(1)" :key="i" class="timeline-variable"></td>
                </tr>
                <tr v-for="(values, varname) in table" :key="varname">
                    <td :class="{ 'timeline-returned-head': 'returned' in scope }">
                        <div class="timeline-var-header">
                            <span>
                                {{ varname }}
                                <md-tooltip md-direction="top">{{ varname }}</md-tooltip>
                            </span>
                            <div class="timeline-var-header-value timeline-variable-value selectable md-elevation-4"
                                :class="current[varname].bool" :style="'background-color: ' + current[varname].color"
                                @mouseover="$emit('highlight', current[varname].line)"
                                @mouseout="$emit('reset')"
                                @click="$emit('show', { varname, index: 0 })">
                                <span v-html="current[varname].icon || current[varname].value"></span>
                            </div>
                        </div>
                    </td>
                    <td v-for="(step, i) in values" :key="i" class="timeline-variable"
                        :class="{ 'timeline-returned-cell': 'returned' in scope && i === 0 }">
                        <div class="timeline-variable-value selectable md-elevation-4" v-if="step"
                            :class="step.bool" :style="'background-color: ' + step.color"
                            @mouseover="$emit('highlight', step.line)"
                            @mouseout="$emit('reset')"
                            @click="$emit('show', { varname, index: step.index })">
                            <span v-html="step.icon || step.value"></span>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
<script>
export default {
    props: ['id', 'scope', 'step'],
    data: function() {
        return {
            current: {},
        }
    },
    methods: {
        scroll: function() {
            const thead = document.getElementById('thead-' + this.id)
            const tbody = document.getElementById('tbody-' + this.id)
            const scrollLeft = tbody.scrollLeft + 'px'
            thead.style.left = '-' + scrollLeft
            thead.children[0].children[0].style.left = scrollLeft
            const rows = tbody.children.length
            for(let i = 0; i < rows; i++) {
                tbody.children[i].children[0].style.left = scrollLeft
            }
        },
        stepValue: function(varname, step) {
            if(this.scope.encoded_vars[varname]['step'] === step)
                return this.scope.encoded_vars[varname]

            const prev_values = this.scope.prev_encoded_vars[varname]
            if(prev_values === undefined) return undefined

            for(let i = 0; i < prev_values.length; i++)
                if(prev_values[i]['step'] === step) return prev_values[i]

            return undefined
        },
    },
    computed: {
        range: function() {
            const temp = this.scope.start || 0
            const start = (this.step - temp) > 100 ? this.step - 100 : temp
            return [...Array(this.step + 1).keys()].slice(start).reverse()
        },
        table: function() {
            this.current = {}
            const table = {}
            this.scope.ordered_varnames.forEach(varname => {
                let index = 0
                const var_entry = []
                this.current[varname] = this.scope['encoded_vars'][varname]

                this.range.forEach(step => {
                    const variable = this.stepValue(varname, step)
                    var_entry.push(variable ? { ...variable, index } : undefined)
                    if(variable) index = index + 1
                })
                table[varname] = var_entry
            })
            return table
        }
    },
}
</script>