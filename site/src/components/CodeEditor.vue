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

    <div class="flex-1 flex flex-col w-full max-h-full" ref="container">
      <div class="editor-container ui-element" ref="aceContainer">
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
import _debounce from 'lodash/debounce'

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
res = sorted(cell.scan(), key=lambda r: (r.position - cell.position).magnitude())
for found in res:
    if type(found) is Nutrient:
        cell.set_destination(found.position)
        print('my pos', cell.position, 'found', found)
        break

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
  mounted() {
    let self = this
    // when ready send initial script
    eventService.bus.on(eventService.events.ON_READY, () => {
      self.onSave()
      self.onPlayPause()
    })
    // on error pause world
    eventService.bus.on(eventService.events.ERROR, self.onError)

    // sometimes on mounted, refs aren't available
    const setResizeObserver = () => {
      if (self.$refs.aceContainer) {
        self.ro = new ResizeObserver(_debounce(self.onResize, 500))
          .observe(self.$refs.aceContainer)
      } else {
        setTimeout(setResizeObserver, 500)
      }
    }
    setResizeObserver()
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
    },
    onResize(e) {
      let self = this
      // setting max height because this is hard to control via css
      // let h = self.$refs.container.clientHeight - self.$refs.aceContainer.clientHeight
      // self.$refs.logger.$refs.logger.style.maxHeight = `${h}px`
    }
  },
  destroyed() {
    let self = this
    delete self.ro
  }
}
</script>

<style lang="sass">

.editor-container
  @apply .p-2 .z-20
  @apply .resize-y .overflow-hidden
  min-height: 100px
  height: 250px

  .error-line
    @apply .bg-red-700 .relative

// for now, let's just do this
.logger
  max-height: 250px

</style>
