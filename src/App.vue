<template>
    <md-app md-mode="fixed">
        <md-app-toolbar class="md-primary" md-theme="default-darker">
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
            <md-button class="md-icon-button md-raised md-dense md-accent" :href="poll.url" target="_blank" v-if="bp[$mq] <= bp.xsmall">
                <md-icon>bar_chart</md-icon>
            </md-button>
            <md-button class="md-raised md-accent" :href="poll.url" target="_blank" v-else>
                <md-icon>poll</md-icon>&ensp;Encuesta de evaluación
            </md-button>
            <stepper class="stepper stepper-bottom"></stepper>
        </md-app-toolbar>
        <md-app-drawer :md-active.sync="showMenu">
            <a id="download-script" style="display: none"></a>
            <md-toolbar class="md-transparent" md-elevation="0">
                Depurador Visual para Python
            </md-toolbar>
            <md-list>
                <li class="md-list-item">
                    <label for="open-file" class="md-list-item-button md-list-item-container md-button-clean">
                        <div class="md-list-item-content md-ripple">
                            <md-icon>insert_drive_file</md-icon>
                            <span class="md-list-item-text">Abrir archivo</span>
                        </div>
                    </label>
                    <input id="open-file" type="file" style="display: none" @change="loadScriptFromFile" accept=".py"/>
                </li>
                <md-list-item id="download-script" @click="showNameDialog = true">
                    <md-icon>save_alt</md-icon>
                    <span class="md-list-item-text">Guardar como...</span>
                </md-list-item>
                <md-list-item md-expand :md-expanded.sync="tutorial.expanded">
                    <md-icon>help</md-icon>
                    <span class="md-list-item-text">Tutorial</span>
                    <md-list slot="md-expand">
                        <md-list-item @click="showTutorial(1)">Editor de código</md-list-item>
                        <md-list-item @click="showTutorial(4)">Consola de E/S</md-list-item>
                        <md-list-item @click="showTutorial(6)">Panel de variables</md-list-item>
                        <md-list-item @click="showTutorial(8)">Expresiones condicionales</md-list-item>
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
                <md-list-item>
                    <md-content class="symbol symbol-assign">
                        <md-icon>edit</md-icon>
                    </md-content>
                    <span class="md-list-item-text">Modificación de variable</span>
                </md-list-item>
            </md-list>
            <md-divider></md-divider>
            <md-list>
                <md-list-item>
                    <md-content class="symbol symbol-bold number">N</md-content>
                    <span class="md-list-item-text">Número</span>
                </md-list-item>
                <md-list-item>
                    <md-content class="symbol symbol-bold string">S</md-content>
                    <span class="md-list-item-text">String o caracter</span>
                </md-list-item>
                <md-list-item>
                    <md-content class="symbol symbol-bold boolean">B</md-content>
                    <span class="md-list-item-text">Lógico (boolean)</span>
                </md-list-item>
                <md-list-item>
                    <md-content class="symbol symbol-bold list">[ ]</md-content>
                    <span class="md-list-item-text">Lista</span>
                </md-list-item>
                <md-list-item>
                    <md-content class="symbol listoflists">
                        <md-icon>format_list_bulleted</md-icon>
                    </md-content>
                    <span class="md-list-item-text">Lista de listas</span>
                </md-list-item>
                <md-list-item>
                    <md-content class="symbol matrix">
                        <md-icon>apps</md-icon>
                    </md-content>
                    <span class="md-list-item-text">Matriz</span>
                </md-list-item>
                <md-list-item>
                    <md-content class="symbol symbol-bold dict">{ }</md-content>
                    <span class="md-list-item-text">Diccionario</span>
                </md-list-item>
                <md-list-item>
                    <md-content class="symbol symbol-bold function">fx()</md-content>
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
                        <img src="@/assets/manual/mobile/condicional-0.png" v-if="tutorial.step === 8">
                        <img src="@/assets/manual/mobile/condicional-1.png" v-if="tutorial.step === 9">
                        <img src="@/assets/manual/mobile/condicional-2.png" v-if="tutorial.step === 10">
                        <img src="@/assets/manual/mobile/fin.png" v-if="tutorial.step === 11">
                    </div>
                    <div class="tutorial-container-image" v-else>
                        <img src="@/assets/manual/desktop/editor-1.png" v-if="tutorial.step === 1">
                        <img src="@/assets/manual/desktop/editor-2.png" v-if="tutorial.step === 2">
                        <img src="@/assets/manual/desktop/editor-3.png" v-if="tutorial.step === 3">
                        <img src="@/assets/manual/desktop/consola-1.png" v-if="tutorial.step === 4">
                        <img src="@/assets/manual/desktop/consola-2.png" v-if="tutorial.step === 5">
                        <img src="@/assets/manual/desktop/variables-1.png" v-if="tutorial.step === 6">
                        <img src="@/assets/manual/desktop/variables-2.png" v-if="tutorial.step === 7">
                        <img src="@/assets/manual/desktop/condicional-0.png" v-if="tutorial.step === 8">
                        <img src="@/assets/manual/desktop/condicional-1.png" v-if="tutorial.step === 9">
                        <img src="@/assets/manual/desktop/condicional-2.png" v-if="tutorial.step === 10">
                        <img src="@/assets/manual/desktop/fin.png" v-if="tutorial.step === 11">
                    </div>
                    <div class="tutorial-container-arrow selectable"
                        v-show="tutorial.step < 11"
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
            <md-dialog-prompt
                :md-active.sync="showNameDialog"
                v-model="fileName"
                md-title="Guardar código a archivo"
                md-input-maxlength="32"
                md-input-placeholder="Ingresa un nombre para el archivo..."
                md-cancel-text="Cancelar"
                md-confirm-text="Guardar"
                @md-confirm="saveFile"/>
            <md-dialog :md-active.sync="poll.show" @md-clicked-outside="resetTimer">
                <md-dialog-title>¡Evalúa las nuevas funcionalidades!</md-dialog-title>
                <md-dialog-content>
                    ¡Gracias por utilizar la aplicación! Por favor, contesta esta <u>breve encuesta</u> 
                    para conocer tu opinión sobre las nuevas funcionalidades. Son cerca de 5 
                    preguntas, no te tomará más de <u>1 minuto</u>!
                </md-dialog-content>
                <md-dialog-actions>
                    <md-button class="md-primary" @click="dismissPoll(false)" :href="poll.url" target="_blank">Sí</md-button>
                    <md-button class="md-primary" @click="resetTimer">Quizás más tarde</md-button>
                    <md-button class="md-primary" @click="dismissPoll(true)">No</md-button>
                </md-dialog-actions>
            </md-dialog>
            <md-dialog-alert
                :md-active.sync="poll.later"
                md-title="Oh... No pasa nada! ;)"
                md-content="Puedes contestar la encuesta en cualquier momento presionando el botón rojo en la <u>esquina superior derecha</u> de la aplicación." />
            <md-dialog :md-active.sync="news.show">
                <md-dialog-title>¡Nuevas funcionalidades!</md-dialog-title>
                <md-dialog-content>
                    <p>
                        Utiliza el panel de <u>Expresiones condicionales</u> para observar en detalle la
                        evaluación de una expresión condicional. Puedes encontrar mayor información en
                        <u>Tutorial > Expresiones condicionales</u>.
                    </p>
                    <img src="@/assets/news/condicional.png" class="md-dialog-image">
                    <p>
                        Ahora puedes abrir y guardar archivos .py en tu dispositivo! Para esto, accede al
                        menú lateral y verás las siguientes opciones:
                    </p>
                    <img src="@/assets/news/files.png" class="md-dialog-image">
                    <p>
                        Si es primera vez que utilizas la aplicación, te invito a ver el <u>Tutorial</u>
                        para conocer más acerca de las características de la plataforma.
                    </p>
                </md-dialog-content>
                <md-dialog-actions>
                    <md-button class="md-primary" @click="news.show = false">Entendido</md-button>
                </md-dialog-actions>
            </md-dialog>
            <md-snackbar class="card-danger" md-position="center" :md-duration="Infinity" :md-active="isOffline" md-theme="default-light" md-persistent>
                <span><u>Se ha perdido la conexión a internet</u>. Los cambios que realices se enviarán para su ejecución una vez que recuperes la conexión...</span>
            </md-snackbar>
            <md-snackbar md-position="center" :md-duration="snack.duration" :md-active.sync="snack.show" md-theme="default-light" :class="snack.className" md-persistent>
                <span v-html="snack.message"></span>
            </md-snackbar>
        </md-app-content>
    </md-app>
</template>
<script>
import Events from '@/events'
import Stepper from '@/components/Stepper'

export default {
    data: function() {
        return {
            contactUrl: 'https://goo.gl/forms/RkbI0jGidSP2DWYn1',
            fileName: '',
            news: {
                show: false,
                tag: 'condicional'
            },
            poll: {
                lapse: 180000, // 3 minutos
                later: false,
                show: false,
                timer: undefined,
                url: 'https://goo.gl/forms/GHc25unyX2eEtuoj2',
            },
            showNameDialog: false,
            showMenu: false,
            snack: {
                className: undefined,
                duration: undefined,
                message: undefined,
                show: false,
            },
            tutorial: {
                expanded: false,
                show: false,
                step: 1,
            },
        }
    },
    components: {
        'stepper': Stepper,
    },
    created: function() {
        this.$root.$on(Events.SHOW_SNACK, this.showSnack)

        const news = localStorage.getItem('news')
        if(news !== this.news.tag) {
            this.news.show = true
            localStorage.setItem('news', this.news.tag)
        }

        // Crea un timer para contestar encuesta, si es que no se ha marcado para "ignorarla"
        const encuesta = localStorage.getItem('encuesta')
        if(encuesta === this.poll.url) return
        this.poll.timer = setTimeout(() => {
            this.poll.show = true
        }, this.poll.lapse)
    },
    methods: {
        dismissPoll: function(later) {
            localStorage.setItem('encuesta', this.poll.url)
            this.poll.show = false
            this.poll.later = later
        },
        loadScriptFromFile: function(ev) {
            const file = ev.target.files[0]
            const reader = new FileReader()
            reader.readAsText(file)
            reader.onload = e => this.$root.$emit(Events.SET_SCRIPT, e.target.result)
            this.showMenu = false
            document.getElementById('open-file').value = ''
        },
        resetTimer: function() {
            clearTimeout(this.poll.timer)
            this.poll.timer = setTimeout(() => {
                this.poll.show = true
            }, this.poll.lapse)
            this.poll.show = false
        },
        saveFile: function() {
            const script = localStorage.getItem('script')
            const blob = new Blob([script], { type: 'text/plain' })
            const a = document.getElementById('download-script')
            a.download = this.fileName + '.py'
            a.href = window.URL.createObjectURL(blob)
            a.click()
            this.fileName = ''
        },
        showMenuTutorial: function() {
            this.tutorial.expanded = true
            this.showMenu = true
        },
        showSnack: function({ className, duration, message }) {
            this.snack.className = className
            this.snack.duration = duration
            this.snack.message = message
            this.snack.show = true
        },
        showTutorial: function(step) {
            this.tutorial.step = step
            this.tutorial.show = true
            this.showMenu = false
        },
    },
}
</script>