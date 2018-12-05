<template>
    <div class="expression expression-container" :style="{ 'background-color': color(depth, true) }">
        <div v-for="(item, i) in parsed" :key="i">
            <div v-if="Array.isArray(item)" class="expression-container">
                <div class="expression-par">(</div>
                <expression :current="current" :depth="depth + 1" :parsed="item" :result="result" :tree="tree + i + '>'" 
                    :class="currentItem(i) ? 'expression-current expression-current-' + item.result : ''"></expression>
                <div class="expression-par">)</div>
            </div>
            <div v-else-if="typeof item === 'object' && '0' in item" class="expression-container" :class="currentItem(i) ? 'expression-current expression-current-' + result : ''">
                <subexpression v-for="(sub, j) in item" :key="j" :item="sub"></subexpression>
            </div>
            <subexpression :item="item" :class="currentItem(i) ? 'expression-current expression-current-' + result : ''" v-else></subexpression>
        </div>
    </div>
</template>
<style lang="scss" src="@/assets/styles/conditional.scss"></style>
<script>
import Methods from '@/components/trace/methods'
import Subexpression from './Subexpression'

export default {
    name: 'expression',
    props: ['current', 'depth', 'parsed', 'result', 'tree'],
    components: {
        'subexpression': Subexpression
    },
    methods: { 
        ...Methods, 
        currentItem: function(index) {
            return this.current === this.tree + index
        }
    },
}
</script>

