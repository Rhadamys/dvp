<template>
    <div>
        <div v-if="scope[index].ordered_varnames.length > 0">
            <md-content class="variable variable-return" v-if="'returned' in scope[index]">
                <md-content class="variable-name">Valor retornado</md-content>
                <var-data :detailed="true" :variable="scope[index].returned" class="variable-values"></var-data>
            </md-content>
            <variable v-for="varname in scope[index].ordered_varnames" :key="varname"
                :current="scope[index].encoded_vars[varname]"
                :prevals="scope[index].prev_encoded_vars[varname]"
                :varname="varname"></variable>
        </div>
        <div v-else>
            <p class="text-center">Aún no se ha definido alguna variable</p>
        </div>
    </div>
</template>
<style lang="scss" src="@/assets/styles/trace.scss"></style>
<script>
import VarData from './variable/VarData'
import Variable from './variable/Variable'

export default {
    props: ['scope'],
    data: function() {
        return {
            index: this.scope.length - 1,
        }
    },
    components: {
        'var-data': VarData,
        'variable': Variable,
    },
    watch: {
        scope: {
            handler() {
                this.index = this.scope.length - 1
            },
            deep: true,
            inmediate: true,
        }
    }
}
</script>
