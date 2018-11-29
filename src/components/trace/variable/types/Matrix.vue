<template>
    <md-table class="variable-matrix md-elevation-4">
        <md-table-row v-for="(row, i) in decode(variable)" :key="i">
            <md-table-cell v-for="(elm, j) in decode(row)" :key="j"
                class="variable-matrix-elm"
                :class="'variable-values-current-' + type(elm)">
                <var-data :variable="elm"></var-data>
                <md-tooltip>Fila: {{ i }}, Columna: {{ j }}</md-tooltip>
            </md-table-cell>
        </md-table-row>
    </md-table>
</template>
<style lang="scss" src="@/assets/styles/variable.scss"></style>
<script>
import Methods from '@/components/trace/methods'

export default {
    props: ['variable'],
    methods: Methods,
}
</script>

