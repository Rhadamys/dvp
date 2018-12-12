<template>
    <div class="trace-scope">
        <div v-if="scope[index].ordered_varnames.length > 0" 
            class="trace-scope" :class="{ 'trace-scope-variables': !timeline }">
            <timeline v-if="timeline" :id="name" :scope="scope[index]" :step="step" 
                    @highlight="highlightLine"
                    @reset="removeHighlight"
                    @show="show" 
                    @step="setStep"></timeline>
            <div v-else>
                <md-content class="variable variable-return" v-if="'returned' in scope[index]">
                    <md-content class="variable-name">Valor retornado</md-content>
                    <var-data :detailed="true" :variable="scope[index].returned" class="variable-values"></var-data>
                </md-content>
                <variable v-for="varname in scope[index].ordered_varnames" :key="varname"
                    :current="scope[index].encoded_vars[varname]"
                    :prevals="scope[index].prev_encoded_vars[varname]"
                    :varname="varname"
                    @highlight="highlightLine"
                    @reset="removeHighlight"
                    @show="show" 
                    @step="setStep"></variable>
            </div>
        </div>
        <div v-else>
            <p class="text-center">Aún no se ha definido alguna variable</p>
        </div>
        <md-dialog :md-active.sync="selection.show" class="variable-dialog">
            <md-dialog-title>
                <div>
                    <span class="md-title">{{ selection.varname }}</span>
                    <md-chip class="md-step">
                        {{ 'Valor asignado en el paso ' + (variable.step + 1) }}
                    </md-chip>
                </div>
                <div class="md-stepping" v-if="selection.max > 0">
                    <md-button class="md-icon-button md-dense"
                        @click="selection.index += 1"
                        :disabled="selection.index === selection.max">
                        <md-icon>navigate_before</md-icon>
                        <md-tooltip md-direction="top">Anterior</md-tooltip>
                    </md-button>
                    <md-button class="md-icon-button md-dense"
                        @click="selection.index -= 1"
                        :disabled="selection.index === 0">
                        <md-icon>navigate_next</md-icon>
                        <md-tooltip md-direction="top">Siguiente</md-tooltip>
                    </md-button>
                </div>
            </md-dialog-title>
            <md-dialog-content>
                <var-data :depth="0" :detailed="true" :variable="variable"></var-data>
            </md-dialog-content>
            <md-dialog-actions>
                <md-button class="md-primary" @click="selection.show = false">Cerrar</md-button>
            </md-dialog-actions>
        </md-dialog>
    </div>
</template>
<script>
import Annotations from '@/annotations'
import Events from '@/events'
import Timeline from './variable/Timeline'
import Variable from './variable/Variable'

export default {
    props: ['name', 'scope', 'step', 'timeline'],
    data: function() {
        return {
            index: this.scope.length - 1,
            selection: {
                index: 0,
                max: 0,
                show: false,
                step: 0,
                varname: '',
            },
            variable: { step: 0 },
        }
    },
    components: {
        'timeline': Timeline,
        'variable': Variable,
    },
    created: function() {
        this.$on('SHOW_VAR', payload => this.show(payload))
    },
    methods: {
        highlightLine: function(line) {
            this.$root.$emit(Events.HIGHLIGHT, {
                row: line - 1,
                column: 0,
                text: '',
                type: Annotations.ASSIGNMENT_LINE
            })
            this.$root.$emit(Events.SCROLL_EDITOR, line)
        },
        removeHighlight: function() {
            this.$root.$emit(Events.REMOVE_LAST_HIGHLIGHT)
        },
        setStep: function(step) {
            this.$root.$emit(Events.SET_STEP, step)
        },
        setVar: function() {
            const scope = this.scope[this.index]
            this.variable =  this.selection.index === -1 ? scope.returned : 
                             this.selection.index === 0 ? scope['encoded_vars'][this.selection.varname] : 
                                                          scope['prev_encoded_vars'][this.selection.varname][this.selection.index - 1]
        },
        show: function({ varname, index }) {
            const name = index >= 0 ? varname : 'Retornado desde: ' + varname
            const prev_values = index >= 0 ? this.scope[this.index]['prev_encoded_vars'][varname] : undefined
            this.selection = Object.assign({}, this.selection, {
                index: index,
                max: prev_values ? prev_values.length : index,
                show: true,
                varname: name,
            })
        },
    },
    watch: {
        scope: {
            handler() {
                this.index = this.scope.length - 1
            },
            deep: true,
            inmediate: true,
        },
        selection: {
            handler() {
                this.setVar()
            },
            deep: true,
            inmediate: true,
        }
    }
}
</script>
