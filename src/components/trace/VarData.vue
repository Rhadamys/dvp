<template>
    <div>
        <div v-if="type(variable) === vartypes.DICT">
            <div :style="{ 'background-color': color() }"
                class="variable-dict">
                <dict v-for="(val, idx) in decode(variable)" :key="idx"
                    :depth="1"
                    :dkey="val[0]"
                    :variable="val[1]"
                    class="md-elevation-4">
                </dict>
            </div>
        </div>
        <div v-else-if="type(variable) === vartypes.LIST">
            <div v-if="variable.length > 0"
                :style="{ 'background-color': color() }"
                class="variable-list">
                <list v-for="(val, idx) in decode(variable)" :key="idx"
                    :depth="1"
                    :index="idx"
                    :variable="val"
                    class="variable-list-item md-elevation-4">
                </list>
            </div>
            <p class="text-center" v-else>Lista vacía</p>
        </div>
        <div v-else-if="type(variable) === vartypes.LIST_OF_LISTS">
            <div v-if="variable.length > 0"
                :style="{ 'background-color': color() }"
                class="variable-list-vertical">
                <list v-for="(val, idx) in decode(variable)" :key="idx"
                    :depth="1"
                    :index="idx"
                    :variable="val"
                    :vertical="true"
                    class="variable-list-vertical-item md-elevation-4">
                </list>
            </div>
            <p class="text-center" v-else>Lista vacía</p>
        </div>
        <div v-else-if="type(variable) === vartypes.MATRIX">
            <md-table class="variable-matrix md-elevation-4">
                <md-table-row v-for="(row, i) in decode(variable)" :key="i">
                    <md-table-cell v-for="(elm, j) in row" :key="j"
                        class="variable-matrix-elm"
                        :class="'variable-values-current-' + type(elm)">
                        <var-data :variable="elm"></var-data>
                        <md-tooltip>Fila: {{ i }}, Columna: {{ j }}</md-tooltip>
                    </md-table-cell>
                </md-table-row>
            </md-table>
        </div>
        <div v-else-if="type(variable) === vartypes.FUNCTION" class="variable-function">
            <div class="gorup-vertical variable-function-identifier md-elevation-4">
                <div class="group-vertical-title">
                    <span>Identificador</span>
                </div>
                <div class="group-vertical-content">{{ decode(variable).name }}</div>
            </div>
            <div class="variable-function-raw">(</div>
            <div class="variable-function-params group-vertical md-evelation-4">
                <div class="group-vertical-title">
                    <span>Parámetros</span>
                </div>
                <div class="group-vertical-content group-horizontal">
                    <div v-for="(param, index) in decode(variable).params" :key="index"
                        class="group-horizontal">
                        <div class="variable-function-param md-elevation-4">
                            <span>{{ param }}</span>
                        </div>
                        <div class="variable-function-raw" v-if="index < decode(variable).params.length - 1">,</div>
                    </div>
                </div>
            </div>
            <div class="variable-function-raw">)</div>
        </div>
        <div v-else>
            <span>{{ value(variable) }}</span>
        </div>
    </div>
</template>
<style lang="scss" src="@/assets/styles/trace.scss"></style>
<script>
import VarTypes from '@/vartypes'
import Methods from '@/components/trace/methods'
import Dictionary from '@/components/trace/Dictionary'
import List from '@/components/trace/List'

export default {
    name: 'var-data',
    props: ['variable'],
    data: function() {
        return {
            vartypes: VarTypes,
        }
    },
    components: {
        'dict': Dictionary,
        'list': List,
    },
    methods: Methods
}
</script>

