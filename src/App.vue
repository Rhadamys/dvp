<template>
    <md-app md-mode="fixed">
        <md-app-toolbar class="md-primary">
            <md-button class="md-icon-button" @click="menuVisible = !menuVisible">
                <md-icon>menu</md-icon>
            </md-button>
            <span class="md-title">Depurador visual para Python</span>
            <stepper class="stepper-bottom"></stepper>
        </md-app-toolbar>
        <md-app-drawer :md-active.sync="menuVisible">
            <md-toolbar class="md-transparent flex-horizontal" md-elevation="0">
                Simbología
                <md-button class="md-icon-button md-raised md-primary"
                    href="https://goo.gl/forms/5FVUR6pIyQaPUii43"
                    target="_blank">
                    <md-icon>poll</md-icon>
                </md-button>
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
            <md-card class="card card-about">
                <md-card-header>
                    <md-avatar>
                        <img src="@/assets/profile.jpg" alt="Imagen de perfil">
                    </md-avatar>
                    <div class="md-title">Mario Álvarez Molina</div>
                    <div class="md-subhead">Estudiante Ingeniería de Ejecución en Computación e Informática</div>
                </md-card-header>
                <md-card-content>
                    Esta aplicación se encuentra en desarrollo y puede presentar inconsistencias. Si tienes alguna sugerencia o comentario, contáctame.
                </md-card-content>
                <md-card-actions>
                    <md-button href="mailto:mario.alvarez.m@usach.cl">
                        <md-icon>mail</md-icon>&ensp;mario.alvarez.m@usach.cl
                    </md-button>
                </md-card-actions>
            </md-card>
        </md-app-drawer>
        <md-app-content>
            <router-view></router-view>
        </md-app-content>
    </md-app>
</template>
<script>
import Stepper from '@/components/Stepper'

export default {
    data: function() {
        return {
            menuVisible: false,
        }
    },
    components: {
        'stepper': Stepper,
    }
}
</script>