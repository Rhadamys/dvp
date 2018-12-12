<template>
    <md-table class="variable-matrix md-elevation-4">
        <md-table-row v-for="(row, i) in variable" :key="i">
            <md-table-cell v-for="(elm, j) in row.value" :key="j"
                class="variable-matrix-elm" :class="elm.type">
                <var-data :variable="elm"></var-data>
                <md-tooltip>Fila: {{ i }}, Columna: {{ j }}</md-tooltip>
            </md-table-cell>
        </md-table-row>
    </md-table>
</template>
<script>
export default {
    props: ['variable'],
}
</script>

