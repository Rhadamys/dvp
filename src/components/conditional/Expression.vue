<template>
    <div class="expression expression-container" :style="{ 'background-color': color(depth) }">
        <div v-for="(item, index) in parsed" :key="index">
            <div v-if="Array.isArray(item)" class="expression-container">
                <div class="expression-par">(</div>
                <expression :current="current" 
                    :depth="depth + 1"
                    :parsed="item"
                    :result="result"
                    :tree="tree + index + '>'"
                    class="expression-inner"></expression>
                <div class="expression-par">)</div>
            </div>
            <expression v-else-if="typeof item === 'object' && '0' in item" 
                :current="current"
                :depth="depth"
                :parsed="item"
                :result="result"
                :tree="tree + index + '>'"
                :class="currentClass(index)"></expression>
            <subexpression :item="item" :class="currentClass(index)" v-else></subexpression>
        </div>
    </div>
</template>
<script>
import Subexpression from './Subexpression'

export default {
    name: 'expression',
    props: ['current', 'depth', 'parsed', 'result', 'tree'],
    components: {
        'subexpression': Subexpression
    },
    methods: {
        color: function(depth = 0) {
            const base = 255 - depth * 30
            return 'rgb(' + base + ', ' + base + ', ' + (base + 10) + ')'
        },
        currentClass: function(index) {
            const is_current = this.currentItem(index)
            const is_bool = typeof this.result === 'boolean'
            return is_current ? 'expression-current expression-current-' + (is_bool ? this.result : 'sub') : ''
        },
        currentItem: function(index) {
            return this.current === this.tree + index
        },
    },
}
</script>

