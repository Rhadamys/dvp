<template>
    <md-app md-mode="fixed">
        <md-app-toolbar class="md-primary">
            <md-button class="md-icon-button" @click="menuVisible = !menuVisible">
                <md-icon>menu</md-icon>
            </md-button>
            <span class="md-title" style="flex: 1">Depurador visual para Python</span>
            <md-button class="md-icon-button md-raised md-dense" :href="pollUrl" target="_blank" v-if="bp[$mq] === bp.xsmall">
                <md-icon>bar_chart</md-icon>
            </md-button>
            <md-button class="md-raised" :href="pollUrl" target="_blank" v-else>
                <md-icon>poll</md-icon>&ensp;Encuesta de evaluación
            </md-button>
            <md-button class="md-icon-button md-raised md-dense md-accent" :href="contactUrl" target="_blank" v-if="bp[$mq] <= bp.small">
                <md-icon>contact_support</md-icon>
            </md-button>
            <md-button class="md-raised md-accent" :href="contactUrl" target="_blank" v-else>
                <md-icon>contact_support</md-icon>&ensp;Informar problema o sugerencia
            </md-button>
            <stepper class="stepper stepper-bottom"></stepper>
        </md-app-toolbar>
        <md-app-drawer :md-active.sync="menuVisible">
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
            contactUrl: 'https://goo.gl/forms/RkbI0jGidSP2DWYn1',
            menuVisible: false,
            pollUrl: 'https://goo.gl/forms/5FVUR6pIyQaPUii43',
        }
    },
    components: {
        'stepper': Stepper,
    }
}
</script>