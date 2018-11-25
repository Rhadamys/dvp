<template>
    <div>
        <md-content class="variable">
            <div class="variable-name">
                {{ varname }}
            </div>
            <div class="variable-values">
                <div class="variable-values-box">
                    <div class="variable-values-box-step">
                        <span>Actual</span>
                    </div>
                    <div class="variable-values-box-value variable-values-current"
                        :class="'variable-values-current-' + type(current)"
                        v-if="type(current) === vartypes.NUMBER || type(current) === vartypes.STRING">
                        {{ current }}
                    </div>
                    <div class="variable-values-box-value variable-values-current selectable"
                        :class="'variable-values-current-' + type(current)"
                        @click="show(varname)"
                        v-html="value(current)" v-else>
                    </div>
                </div>
                <div v-if="prevals" class="variable-values">
                    <div class="variable-values-box variable-values-prev selectable"
                        v-if="prevals.length > prevalsRange.max && prevalsRange.start > 0"
                        @click="prevalsRange.start -= 1">
                        <md-icon>navigate_before</md-icon>
                        <md-tooltip md-direction="left">Más recientes...</md-tooltip>
                    </div>
                    <div v-for="(prev, index) in subprevals" :key="index" class="variable-values-box list-complete-item">
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
                    <div class="variable-values-box variable-values-prev selectable"
                        v-if="prevals.length > prevalsRange.max && prevalsRange.start < prevals.length - prevalsRange.max - 1"
                        @click="prevalsRange.start += 1">
                        <md-icon>navigate_next</md-icon>
                        <md-tooltip md-direction="left">Anteriores...</md-tooltip>
                    </div>
                </div>
            </div>
        </md-content>
        <md-dialog :md-active.sync="showDialog">
            <md-dialog-title>
                <div>
                    <span class="md-title">{{ varname }}</span>
                    <md-chip class="md-step">
                        {{ index === 0 ? 'Valor actual' : 'Valor hasta el paso ' + variable.step }}
                    </md-chip>
                </div>
                <div class="md-stepping" v-if="prevals">
                    <md-button class="md-icon-button md-dense"
                        @click="index += 1"
                        v-bind:disabled="index === prevals.length">
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
    props: ['current', 'prevals', 'varname'],
    data: function() {
        return {
            index: undefined,
            prevalsRange: {
                max: window.isMobile() ? 3: 6,
                start: 0,
            },
            showDialog: false,
            variable: {
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
            this.index = index === undefined ? 0 : index + 1
            this.setVar()
            this.showDialog = true
        },
        setStep: function(step) {
            this.$root.$emit(Events.SET_STEP, step)
        },
        setVar: function() {
            if(this.prevals) {
                const selected = this.index > 0 ? this.prevals[this.index - 1] : current
                const value = selected.value || selected
                this.variable.step = selected.step
                this.variable.value = value
            } else
                this.variable.value = this.decode(variable)
        },
    },
    computed: {
        subprevals: function() {
            return this.prevals.slice(this.prevalsRange.start, this.prevalsRange.start + this.prevalsRange.max)
        }
    },
    watch: {
        index: function() {
            this.setVar()
        },
    }
}
</script>