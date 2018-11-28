<template>
    <md-app md-mode="fixed">
        <md-app-toolbar class="md-primary">
            <md-button class="md-icon-button" @click="showMenu = !showMenu">
                <md-icon>menu</md-icon>
            </md-button>
            <span class="md-title" style="flex: 1">Depurador visual para Python</span>
            <md-button class="md-icon-button md-raised md-dense" @click="showMenuTutorial" v-if="bp[$mq] <= bp.xsmall">
                <md-icon>help</md-icon>
            </md-button>
            <md-button class="md-raised" @click="showMenuTutorial" v-else>
                <md-icon>help</md-icon>&ensp;Tutorial
            </md-button>
            <md-button class="md-icon-button md-raised md-dense md-accent" :href="pollUrl" target="_blank" v-if="bp[$mq] <= bp.xsmall">
                <md-icon>bar_chart</md-icon>
            </md-button>
            <md-button class="md-raised md-accent" :href="pollUrl" target="_blank" v-else>
                <md-icon>poll</md-icon>&ensp;Encuesta de evaluación
            </md-button>
            <stepper class="stepper stepper-bottom"></stepper>
        </md-app-toolbar>
        <md-app-drawer :md-active.sync="showMenu">
            <md-toolbar class="md-transparent" md-elevation="0">
                Depurador Visual para Python
            </md-toolbar>
            <md-list>
                <md-list-item md-expand :md-expanded.sync="tutorial.expanded">
                    <md-icon>help</md-icon>
                    <span class="md-list-item-text">Tutorial</span>
                    <md-list slot="md-expand">
                        <md-list-item @click="showTutorial(1)">Editor de código</md-list-item>
                        <md-list-item @click="showTutorial(4)">Consola de E/S</md-list-item>
                        <md-list-item @click="showTutorial(6)">Panel de variables</md-list-item>
                    </md-list>
                </md-list-item>
            </md-list>
            <md-toolbar class="md-transparent" md-elevation="0">
                Simbología
            </md-toolbar>
            <md-list>
                <md-list-item>
                    <md-content class="symbol symbol-current">
                        <md-icon>navigate_next</md-icon>
                    </md-content>
                    <span class="md-list-item-text">Línea actual en ejecución</span>
                </md-list-item>
                <md-list-item>
                    <md-content class="symbol symbol-next">
                        <md-icon>navigate_next</md-icon>
                    </md-content>
                    <span class="md-list-item-text">Línea siguiente en la ejecución</span>
                </md-list-item>
                <md-list-item>
                    <md-content class="symbol symbol-error">
                        <md-icon>error</md-icon>
                    </md-content>
                    <span class="md-list-item-text">Error (Excepción no controlada de la aplicación)</span>
                </md-list-item>
                <md-list-item>
                    <md-content class="symbol symbol-warning">
                        <md-icon>warning</md-icon>
                    </md-content>
                    <span class="md-list-item-text">Advertencia (Excepción controlada)</span>
                </md-list-item>
                <md-list-item>
                    <md-content class="symbol symbol-prompt">
                        <md-icon>keyboard</md-icon>
                    </md-content>
                    <span class="md-list-item-text">Entrada de usuario requerida en la consola</span>
                </md-list-item>
            </md-list>
            <md-divider></md-divider>
            <md-list>
                <md-list-item>
                    <md-content class="symbol symbol-bold variable-values-current-number">N</md-content>
                    <span class="md-list-item-text">Número</span>
                </md-list-item>
                <md-list-item>
                    <md-content class="symbol symbol-bold variable-values-current-string">S</md-content>
                    <span class="md-list-item-text">String y caracter</span>
                </md-list-item>
                <md-list-item>
                    <md-content class="symbol symbol-bold variable-values-current-list">[]</md-content>
                    <span class="md-list-item-text">Lista</span>
                </md-list-item>
                <md-list-item>
                    <md-content class="symbol variable-values-current-listoflists">
                        <md-icon>format_list_bulleted</md-icon>
                    </md-content>
                    <span class="md-list-item-text">Lista de listas</span>
                </md-list-item>
                <md-list-item>
                    <md-content class="symbol variable-values-current-matrix">
                        <md-icon>apps</md-icon>
                    </md-content>
                    <span class="md-list-item-text">Matriz</span>
                </md-list-item>
                <md-list-item>
                    <md-content class="symbol symbol-bold variable-values-current-function">fx()</md-content>
                    <span class="md-list-item-text">Función</span>
                </md-list-item>
            </md-list>
            <md-divider></md-divider>
            <md-card class="card card-about">
                <md-card-header>
                    <md-avatar>
                        <img src="@/assets/profile.jpg" alt="Imagen de perfil">
                    </md-avatar>
                    <div class="md-title">Mario Álvarez Molina</div>
                    <div class="md-subhead">Estudiante Ingeniería de Ejecución en Computación e Informática</div>
                </md-card-header>
                <md-card-content>
                    Esta aplicación se encuentra en desarrollo y puede presentar inconsistencias. Si tienes alguna sugerencia o quieres informar un error, utiliza el formulario a continuación.
                </md-card-content>
                <md-card-actions>
                    <md-button :href="contactUrl" target="_blank">
                        <md-icon>contact_support</md-icon>&ensp;Informar error o sugerencia
                    </md-button>
                </md-card-actions>
            </md-card>
        </md-app-drawer>
        <md-app-content>
            <div class="tutorial" v-if="tutorial.show">
                <div class="tutorial-container">
                    <div class="tutorial-container-arrow selectable"
                        v-show="tutorial.step > 1"
                        @click="tutorial.step -= 1">
                        <md-icon>navigate_before</md-icon>
                    </div>
                    <div class="tutorial-container-image" v-if="bp[$mq] <= bp.xsmall">
                        <img src="@/assets/manual/mobile/editor-1.png" v-if="tutorial.step === 1">
                        <img src="@/assets/manual/mobile/editor-2.png" v-if="tutorial.step === 2">
                        <img src="@/assets/manual/mobile/editor-3.png" v-if="tutorial.step === 3">
                        <img src="@/assets/manual/mobile/consola-1.png" v-if="tutorial.step === 4">
                        <img src="@/assets/manual/mobile/consola-2.png" v-if="tutorial.step === 5">
                        <img src="@/assets/manual/mobile/variables-1.png" v-if="tutorial.step === 6">
                        <img src="@/assets/manual/mobile/variables-2.png" v-if="tutorial.step === 7">
                        <img src="@/assets/manual/mobile/fin.png" v-if="tutorial.step === 8">
                    </div>
                    <div class="tutorial-container-image" v-else>
                        <img src="@/assets/manual/desktop/editor-1.png" v-if="tutorial.step === 1">
                        <img src="@/assets/manual/desktop/editor-2.png" v-if="tutorial.step === 2">
                        <img src="@/assets/manual/desktop/editor-3.png" v-if="tutorial.step === 3">
                        <img src="@/assets/manual/desktop/consola-1.png" v-if="tutorial.step === 4">
                        <img src="@/assets/manual/desktop/consola-2.png" v-if="tutorial.step === 5">
                        <img src="@/assets/manual/desktop/variables-1.png" v-if="tutorial.step === 6">
                        <img src="@/assets/manual/desktop/variables-2.png" v-if="tutorial.step === 7">
                        <img src="@/assets/manual/desktop/fin.png" v-if="tutorial.step === 8">
                    </div>
                    <div class="tutorial-container-arrow selectable"
                        v-show="tutorial.step < 8"
                        @click="tutorial.step += 1">
                        <md-icon>navigate_next</md-icon>
                    </div>
                </div>
                <div class="tutorial-actions">
                    <md-button class="md-primary md-raised" @click="tutorial.show = false">Cerrar</md-button>
                </div>
            </div>
            <transition name="component-fade" mode="out-in">
                <router-view></router-view>
            </transition>
        </md-app-content>
    </md-app>
</template>
<style lang="scss" src="@/assets/styles/variable.scss"></style>
<script>
import Stepper from '@/components/Stepper'

export default {
    data: function() {
        return {
            contactUrl: 'https://goo.gl/forms/RkbI0jGidSP2DWYn1',
            pollUrl: 'https://goo.gl/forms/5FVUR6pIyQaPUii43',
            showMenu: false,
            tutorial: {
                expanded: true,
                show: false,
                step: 1,
            },
        }
    },
    components: {
        'stepper': Stepper,
    },
    methods: {
        showMenuTutorial: function() {
            this.tutorial.expanded = true
            this.showMenu = true
        },
        showTutorial: function(step) {
            this.tutorial.step = step
            this.tutorial.show = true
            this.showMenu = false
        }
    }
}
</script>