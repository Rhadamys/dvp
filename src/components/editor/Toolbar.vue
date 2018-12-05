<template>
    <md-card-actions md-alignment="space-between">
        <div class="editor-exc">
            <md-button class="editor-exc-errors md-dense" @click="showExceptionsDialog = true"
                v-bind:disabled="exceptions.errors.length === 0">
                <md-icon>error</md-icon>&ensp;{{ exceptions.errors.length }}
                <md-tooltip md-direction="top">Errores</md-tooltip>
            </md-button>
            <md-button class="editor-exc-warnings md-dense" @click="showExceptionsDialog = true"
                v-bind:disabled="exceptions.warnings.length === 0">
                <md-icon>warning</md-icon>&ensp;{{ exceptions.warnings.length }}
                <md-tooltip md-direction="top">Advertencias</md-tooltip>
            </md-button>
        </div>
        <div class="editor-actions">
            <md-button class="md-icon-button md-dense"
                @click="emitRender(stepping.current - 1)"
                v-bind:disabled="stepping.current === 0"
                v-if="stepping.last">
                <md-icon>navigate_before</md-icon>
                <md-tooltip md-direction="top">Retroceder</md-tooltip>
            </md-button>
            <md-button class="md-icon-button md-dense"
                @click="emitRender(stepping.current + 1)"
                v-bind:disabled="stepping.current === stepping.last"
                v-if="stepping.last">
                <md-icon>navigate_next</md-icon>
                <md-tooltip md-direction="top">Avanzar</md-tooltip>
            </md-button>
            <md-button class="md-icon-button md-dense"
                @click="refresh"
                v-if="isOnline">
                <md-icon>refresh</md-icon>
                <md-tooltip md-direction="top">Volver a ejecutar</md-tooltip>
            </md-button>
        </div>
        <md-dialog :md-active.sync="showExceptionsDialog">
            <md-card class="card card-error" md-theme="default-light">
                <md-card-header>
                    <span class="md-title">
                        <md-icon>error</md-icon>&ensp;Errores
                    </span>
                </md-card-header>
                <md-table v-model="exceptions.errors" md-sort="step" md-sort-order="asc"
                    v-if="exceptions.errors.length > 0"
                    @md-selected="gotoStep" md-card>
                    <md-table-row slot="md-table-row" slot-scope="{ item }" md-selectable="single">
                        <md-table-cell md-label="Paso" md-sort-by="step" md-numeric>{{ item.step }}</md-table-cell>
                        <md-table-cell md-label="Línea" md-sort-by="lineno" md-numeric>{{ item.lineno }}</md-table-cell>
                        <md-table-cell md-label="Descripción" md-sort-by="message">{{ item.message }}</md-table-cell>
                    </md-table-row>
                </md-table>
                <p class="text-center" v-else>No se ha encontrado errores</p>
            </md-card>
            <md-card class="card card-warning" md-theme="default-light">
                <md-card-header>
                    <span class="md-title">
                        <md-icon>warning</md-icon>&ensp;Advertencias
                    </span>
                </md-card-header>
                <md-table v-model="exceptions.warnings" md-sort="step" md-sort-order="asc"
                    v-if="exceptions.warnings.length > 0"
                    @md-selected="gotoStep" md-card>
                    <md-table-row slot="md-table-row" slot-scope="{ item }" md-selectable="single">
                        <md-table-cell md-label="Paso" md-sort-by="step" md-numeric>{{ item.step }}</md-table-cell>
                        <md-table-cell md-label="Línea" md-sort-by="lineno" md-numeric>{{ item.lineno }}</md-table-cell>
                        <md-table-cell md-label="Descripción" md-sort-by="message">{{ item.message }}</md-table-cell>
                    </md-table-row>
                </md-table>
                <p class="text-center" v-else>No se ha encontrado advertencias</p>
            </md-card>
            <md-dialog-actions>
                <md-button class="md-primary" @click="showExceptionsDialog = false">Cerrar</md-button>
            </md-dialog-actions>
        </md-dialog>
    </md-card-actions>
</template>
<style lang="scss" src="@/assets/styles/editor.scss"></style>
<style lang="scss" src="@/assets/styles/trace.scss"></style>
<script>
import Events from '@/events'
import Stepper from '@/components/Stepper'

export default {
    props: ['exceptions', 'stepping'],
    data: function() {
        return {
            /**
             * Toggle para ver / ocultar el diálogo en que se muestran los errores y
             * excepciones encontradas.
             */
            showExceptionsDialog: false,
        }
    },
    components: {
        'stepper': Stepper,
    },
    methods: {
        emitRender: function(step) {
            this.$root.$emit(Events.SET_STEP, step)
        },
        /**
         * Al seleccionar una excepción desde el diálogo de excepciones, la ejecución
         * se mueve al paso donde se produjo.
         * @param exception Excepción seleccionada en la lista
         */
        gotoStep: function(exception) {
            this.showExceptionsDialog = false
            this.$root.$emit(Events.SET_STEP, exception.step)
        },
        /**
         * Vuelve a ejecutar el código. Esto es útil cuando se han ingresado datos, de esta
         * forma los volverá a solicitar.
         */
        refresh: function() {
            this.$root.$emit(Events.RESET)
            this.$root.$emit(Events.SEND_SCRIPT)
        },
    }
}
</script>