<template>
    <div class="expression-container">
        <div class="conditional-variable md-elevation-4" v-if="item.type === itemTypes.VARIABLE">
            <div class="conditional-variable-name">
                <span>{{ item.part }}</span>
                <md-tooltip md-direction="top">{{ item.part }}</md-tooltip>
            </div>
            <div class="conditional-variable-value" :class="'variable-values-current-' + type(item.value)">
                <var-data :variable="item.value"></var-data>
            </div>
        </div>
        <div class="conditional-function md-elevation-4" v-else-if="item.type === itemTypes.FUNCTION">
            <div class="conditional-function-name">{{ item.part }}</div>
            <div class="conditional-function-par">(</div>
            <div class="conditional-function-params">
                <div :class="'expression-item-' + item.type" v-for="(param, k) in item.params" :key="k">
                    {{ param.part }}
                </div>
                <div class="conditional-function-comma">,</div>
            </div>
            <div class="conditional-function-par">)</div>
            <div class="conditional-function-par">=</div>
            <div class="conditional-function-result" :class="'variable-values-current-' + type(item.result)">
                <var-data :variable="item.result"></var-data>
            </div>
        </div>
        <div class="expression-item md-elevation-4"
            :class="['expression-item-' + item.type, { 'selectable' : item.type === itemTypes.LOGICAL }]" v-else>
            {{ item.part }}
            <md-tooltip md-direction="top" v-if="item.type === 'or-skipped'">No se evaluó debido a que la <u>primera expresión ya es verdadera</u></md-tooltip>
        </div>
    </div>
</template>
<style lang="scss" src="@/assets/styles/conditional.scss"></style>
<script>
import Methods from '@/components/trace/methods'

export default {
    props: ['item'],
    data: function() {
        return {
            itemTypes: {
                FUNCTION: 'function',
                LOGICAL: 'logical',
                VARIABLE: 'variable',
            }
        }
    },
    methods: Methods,
}
</script>
