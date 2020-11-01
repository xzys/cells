<template>
  <div class="flex flex-col flex-1">
    <div class="buttons-row flex mb-2">
      <div class="button w-24"
        @click="onPlayPause">
        <IconPlay class="icon" v-if="paused" />
        <IconPause class="icon" v-else />
        {{ paused ? 'Play' : 'Pause'}}
      </div>

      <div class="flex-1"></div>
      <div class="button-icon"
        v-if="scriptModified"
        @click="onSave">
        <IconRefresh class="icon"/>
      </div>
      <div class="button-icon button-inactive">
        <IconHand class="icon"/>
      </div>
    </div>

    <div class="flex-1 flex flex-col w-full max-h-full">
      <div class="editor-container ui-element">
        <AceEditor ref="ace"
          @init="editorInit"
          lang="python"
          theme="dracula"
          width="100%" height="100%"
          v-model="value"
          />
      </div>
      <Logger ref="logger"
        />
    </div>
  </div>
</template>

<script>
import IconPlay from 'heroicons/outline/play.svg'
import IconPause from 'heroicons/outline/pause.svg'
// import IconBeaker from 'heroicons/outline/beaker.svg'
import IconHand from 'heroicons/outline/hand.svg'
import IconRefresh from 'heroicons/outline/save.svg'
import AceEditor from 'vue2-ace-editor'
import Logger from './Logger'
import eventService from '../services/eventService'

let ace = require('brace')
let Range = ace.acequire('ace/range').Range


export default {
  name: 'CodeEditor',
  components: {
    AceEditor, Logger,
    IconPlay, IconPause, IconRefresh, IconHand,
  },
  data() {
    const defaultScript = (`
print('my pos', cell.position)
print(1/0)
for found in cell.scan():
    if type(found) is Nutrient:
        cell.set_destination(found.position)

if cell.size > 100:
   cell.divide()`).trim()

    return {
      lastValue: defaultScript,
      value: defaultScript,

      errorMarker: null,
      paused: true,
    }
  },
  computed: {
    scriptModified() {
      let self = this
      return self.lastValue !== self.value
    }
  },
  created() {
    let self = this
    // when ready send initial script
    eventService.bus.on(eventService.events.ON_READY, () => {
      self.onSave()
      self.onPlayPause()
    })
    // on error pause world
    eventService.bus.on(eventService.events.ERROR, self.onError)
  },
  methods: {
    editorInit() {
      require('brace/ext/language_tools')
      require('brace/mode/python')                
      require('brace/theme/dracula')
    },
    onSave() {
      let self = this
      self.$refs.logger.error = null
      self.lastValue = self.value
      self.clearError()
      eventService.bus.emit(eventService.events.MODIFY_SCRIPT, self.value)
    },
    onPlayPause() {
      let self = this
      self.paused = !self.paused
      const e = self.paused ?
        eventService.events.PAUSE_WORLD :
        eventService.events.PLAY_WORLD
      eventService.bus.emit(e)
    },
    onError(lines, ctx) {
      let self = this
      if (!self.paused) {
        self.onPlayPause()
      }
      self.clearError()
      self.errorMarker = self.$refs.ace.editor.session.addMarker(
        new Range(ctx.line-1, 0, ctx.line-1, Infinity), "error-line", "fullLine"
      )
    },
    clearError() {
      let self = this
      if (self.errorMarker !== null) {
        self.$refs.ace.editor.session.removeMarker(self.errorMarker)
        self.errorMarker = null
      }
    }
  }
}
</script>

<style lang="sass">

.editor-container
  @apply .p-2 .z-20
  @apply .overflow-hidden .resize-y
  height: 50%

  .error-line
    @apply .bg-red-700 .relative


</style>
