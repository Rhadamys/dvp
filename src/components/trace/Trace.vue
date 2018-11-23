<template>
    <md-card class="trace">
        <md-tabs class="md-primary" v-if="torender">
            <md-tab v-for="(scope, index) in torender" :key="index"
                :id="'tab-scope-' + index"
                :md-label="scope.func_name">
                <div v-if="scope.ordered_varnames.length > 0">
                    <variable :scope="scope"></variable>
                </div>
                <div v-else>
                    <p class="text-center">Aún no se ha definido alguna variable</p>
                </div>
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
import VarTypes from '@/vartypes'
import VarData from '@/components/trace/VarData'
import Variable from '@/components/trace/Variable'

export default {
    props: ['stack'],
    data: function() {
        return {
            torender: undefined,
        }
    },
    components: {
        'var-data': VarData,
        'variable': Variable,
    },
    watch: {
        stack: {
            handler() {
                this.torender = undefined
                const torender = []
                for(var i = 0; i < this.stack.length; i++) {
                    const scope = this.stack[i]
                    if(scope.ordered_varnames.includes(VarTypes.RETURN)) {
                        scope.ordered_varnames.pop()
                        const ret = scope.encoded_vars[VarTypes.RETURN]
                        delete scope.encoded_vars[VarTypes]
                        scope.returned = ret
                    }
                    torender.push(scope)
                }
                this.torender = Object.assign([], this.torender, torender)
                console.log('HANDLEDDDDDDDDD')
            },
            deep: true,
            immediate: true,
        }
    }
}
</script>