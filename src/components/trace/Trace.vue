<template>
    <md-card class="trace" :class="{ 'trace-minimized': hide && !expanded }">
        <md-tabs class="md-primary" v-if="stack.order.length > 0" :md-active-tab="current" @md-changed="current = $event">
            <md-tab v-for="scope_name in stack.order" :key="scope_name" :id="scope_name" :md-label="tagName(scope_name)">
                <scope :name="scope_name" :scope="stack.scopes[scope_name]" :step="step" :timeline="timeline"></scope>
            </md-tab>
        </md-tabs>
        <md-card-content v-else-if="!hide || expanded">
            <p class="text-center">Aún no se ha definido alguna variable</p>
        </md-card-content>
        <md-button class="md-dense trace-button trace-button-alternate" @click="timeline = !timeline" v-if="timeline">
            <md-icon >view_list</md-icon>
            <md-tooltip v-if="!isMobile()" md-direction="left">Ver agrupado</md-tooltip>
        </md-button>
        <md-button class="md-dense trace-button trace-button-alternate" @click="timeline = !timeline" v-else>
            <md-icon>timeline</md-icon>
            <md-tooltip v-if="!isMobile()" md-direction="left">Ver como línea de tiempo</md-tooltip>
        </md-button>
        <md-button class="md-dense trace-button trace-button-sizing" @click="$emit('resize')">
            <md-icon v-if="expanded">keyboard_arrow_down</md-icon>
            <md-icon v-else-if="hide">remove</md-icon>
            <md-icon v-else>keyboard_arrow_up</md-icon>
            <md-tooltip v-if="!isMobile()" md-direction="left">
                {{ expanded ? messages.minimize : hide ? messages.neutral : messages.maximize }}
            </md-tooltip>
        </md-button>
    </md-card>
</template>
<script>
import Const from '@/const'
import Events from '@/events'
import Scope from './Scope'

export default {
    props: ['hide', 'expanded', 'step'],
    data: function() {
        return {
            current: '',
            messages: Const.SIZING_MESSAGES,
            stack: {
                order: [], 
                scopes: [] 
            },
            timeline: false,
        }
    },
    components: {
        'scope': Scope,
    },
    created: function() {
        this.$root.$on(Events.SET_TRACE, stack => this.stack = stack)
        this.$root.$on(Events.RESET, this.reset)
    },
    methods: {
        active: function(tab) {
            console.log('-----------------')
            console.log(tab)
        },
        tagName: function(name) {
            const len = this.stack.scopes[name].length
            return name + (name === 'global' || len <= 1 ? '' :  ' (' + len + ')')
        },
        reset: function() {
            this.stack = Object.assign({}, this.stack, { order: [], scopes: {} })
        }
    },
    watch: {
        step: function() {
            if(this.stack.order.includes(this.current)) return
            this.current = 'global'
        }
    }
}
</script>