<template>
    <div>
        <md-content class="variable variable-return" v-if="scope.returned">
            <md-content class="variable-name">Valor retornado</md-content>
            <var-data :variable="scope.returned"
                class="variable-values"></var-data>
        </md-content>
        <md-content class="variable" v-for="varname in scope.ordered_varnames" :key="varname">
            <div class="variable-name">
                {{ varname }}
            </div>
            <div class="variable-values">
                <div class="variable-values-box">
                    <div class="variable-values-box-step">
                        <span>Actual</span>
                    </div>
                    <div class="variable-values-box-value variable-values-current"
                        :class="'variable-values-current-' + type(scope.encoded_vars[varname])"
                        v-if="type(scope.encoded_vars[varname]) === vartypes.NUMBER || type(scope.encoded_vars[varname]) === vartypes.STRING">
                        {{ scope.encoded_vars[varname] }}
                    </div>
                    <div class="variable-values-box-value variable-values-current selectable"
                        :class="'variable-values-current-' + type(scope.encoded_vars[varname])"
                        @click="show(varname)"
                        v-html="value(scope.encoded_vars[varname])" v-else>
                    </div>
                </div>
                <div v-if="scope.prev_encoded_vars"
                    v-for="(prev, index) in scope.prev_encoded_vars[varname]" :key="index"
                    class="variable-values-box">
                    <div class="variable-values-box-step selectable">
                        <span @click="setStep(prev.step - 1)">{{ prev.step }}</span>
                    </div>
                    <div class="variable-values-box-value variable-values-prev"
                        :class="'variable-values-prev-' + type(prev.value)"
                        v-if="type(prev.value) === vartypes.NUMBER || type(prev.value) === vartypes.STRING">
                        {{ prev.value }}
                    </div>
                    <div class="variable-values-box-value variable-values-prev selectable"
                        :class="'variable-values-prev-' + type(prev.value)"
                        @click="show(varname, index)"
                        v-html="value(prev.value)" v-else>
                    </div>
                </div>
            </div>
        </md-content>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title>
                <div>
                    <span class="md-title">{{ variable.name }}</span>
                    <md-chip class="md-step">
                        {{ index === 0 ? 'Valor actual' : 'Valor hasta el paso ' + variable.step }}
                    </md-chip>
                </div>
                <div class="md-stepping" v-if="scope.prev_encoded_vars[variable.name]">
                    <md-button class="md-icon-button md-dense"
                        @click="index += 1"
                        v-bind:disabled="index === scope.prev_encoded_vars[variable.name].length">
                        <md-icon>navigate_before</md-icon>
                        <md-tooltip md-direction="top">Anterior</md-tooltip>
                    </md-button>
                    <md-button class="md-icon-button md-dense"
                        @click="index -= 1"
                        v-bind:disabled="index === 0">
                        <md-icon>navigate_next</md-icon>
                        <md-tooltip md-direction="top">Siguiente</md-tooltip>
                    </md-button>
                </div>
            </md-dialog-title>
            <md-dialog-content>
                <var-data :variable="variable.value"></var-data>
            </md-dialog-content>
            <md-dialog-actions>
                <md-button class="md-primary" @click="showDialog = false">Cerrar</md-button>
            </md-dialog-actions>
        </md-dialog>
    </div>
</template>
<style lang="scss" src="@/assets/styles/trace.scss"></style>
<script>
import Events from '@/events'
import VarTypes from '@/vartypes'
import Methods from '@/components/trace/methods'
import VarData from '@/components/trace/VarData'

export default {
    props: ['scope'],
    data: function() {
        return {
            index: undefined,
            showDialog: false,
            variable: {
                name: undefined,
                step: undefined,
                value: undefined,
            },
            vartypes: VarTypes,
        }
    },
    components: {
        'var-data': VarData,
    },
    methods: {
        ...Methods,
        show: function(varname, index) {
            this.variable.name = varname
            this.index = index === undefined ? 0 : index + 1
            this.setVar()
            this.showDialog = true
        },
        setStep: function(step) {
            this.$root.$emit(Events.SET_STEP, step)
        },
        setVar: function() {
            const variable = this.index > 0 ? this.scope.prev_encoded_vars[this.variable.name] : 
                                              this.scope.encoded_vars[this.variable.name]
            if(this.scope.prev_encoded_vars) {
                const len = this.scope.prev_encoded_vars.length
                const selected = this.index > 0 ? variable[this.index - 1] : variable
                const value = selected.value || selected
                this.variable.step = selected.step
                this.variable.value = value
            } else
                this.variable.value = this.decode(variable)
        },
    },
    watch: {
        index: function() {
            this.setVar()
        },
    }
}
</script>