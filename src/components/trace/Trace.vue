<template>
    <md-card class="trace">
        <md-tabs class="md-primary" v-if="stack.order.length > 0">
            <md-tab v-for="(scope_name, index) in stack.order" :key="index"
                :id="'tab-scope-' + index"
                :md-label="tagName(scope_name)">
                <scope :scope="stack.scopes[scope_name]"></scope>
            </md-tab>
        </md-tabs>
        <md-card-content v-else>
            <p class="text-center">Aún no se ha definido alguna variable</p>
        </md-card-content>
    </md-card>
</template>
<style lang="scss" src="@/assets/styles/trace.scss"></style>
<script>
import Events from '@/events'
import Scope from './Scope'

export default {
    data: function() {
        return {
            stack: {
                order: [], 
                scopes: [] 
            },
        }
    },
    components: {
        'scope': Scope,
    },
    created: function() {
        this.$root.$on(Events.SET_TRACE, this.decodeTrace)
        this.$root.$on(Events.RESET, this.reset)
    },
    methods: {
        decodeTrace: function(stack) {
            if(stack == undefined) return
            const temp_stack = { order: [], scopes: {} }
            stack.ordered_scopes.forEach(scope_name => {
                const scope = stack[scope_name]
                let scope_entries = []
                if(scope_name === 'global') 
                    scope_entries.push(scope)
                else {
                    scope.ordered_hashes.forEach(hash => {
                        scope_entries.push(scope[hash])
                    })
                }
                temp_stack.scopes[scope_name] = scope_entries
            })
            temp_stack.order = stack.ordered_scopes
            this.stack = Object.assign({}, this.stack, temp_stack)
        },
        tagName: function(name) {
            const len = this.stack.scopes[name].length
            return name + (name === 'global' || len <= 1 ? '' :  ' (' + len + ')')
        },
        reset: function() {
            this.stack = Object.assign({}, this.stack, { order: [], scopes: {} })
        }
    },
}
</script>