<template>
  <div class="code-editor-pane flex flex-col flex-1">
    <!--
    <div class="buttons-row flex mb-2">
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
    -->

    <div class="flex-1 flex flex-col w-full max-h-full" ref="container">
      <div class="pane-header">
        <div class="text-button float-right"
          >save</div>
      </div>
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
// import IconBeaker from 'heroicons/outline/beaker.svg'
// import IconHand from 'heroicons/outline/hand.svg'
// import IconRefresh from 'heroicons/outline/save.svg'
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
    // IconRefresh, IconHand,
  },
  data() {
    let defaultScript = (`
res = sorted(cell.scan(), key=lambda r: (r.position - cell.position).magnitude())
for found in res:
    if type(found) is Nutrient:
        cell.set_destination(found.position)
        print('my pos', cell.position, 'found', found)
        break

if cell.size > 100:
   cell.divide()`).trim()
    defaultScript = '# write your code here'

    return {
      lastValue: defaultScript,
      value: defaultScript,

      errorMarker: null,
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
    // on error pause world
    eventService.bus.on(eventService.events.ERROR, self.onError)
    // 
    eventService.bus.on(eventService.events.SET_DEST, self.setDestination)

    // sometimes on mounted, refs aren't available
    /*
    const setResizeObserver = () => {
      if (self.$refs.aceContainer) {
        self.ro = new ResizeObserver(_debounce(self.onResize, 500))
          .observe(self.$refs.aceContainer)
      } else {
        setTimeout(setResizeObserver, 500)
      }
    }
    setResizeObserver()
    */
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
      eventService.bus.emit(eventService.events.MODIFY_SCRIPT, self.value)
      self.clearError()
    },
    setDestination(x, y) {
      let self = this
      let lines = self.value.split('\n')
      const stmt = `cell.set_destination(${x}, ${y}) # set from click`
      if (lines[lines.length - 1].startsWith('cell.set_destination')) {
        lines[lines.length - 1] = stmt
      } else {
        lines.push(stmt)
      }
      self.value = lines.join('\n')
      self.onSave()
    },
    onError(lines, ctx) {
      let self = this
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

.code-editor-pane
  @apply .pointer-events-auto

  .editor-container
    @apply .p-2 .z-20
    @apply .resize-y .overflow-hidden
    min-height: 100px
    height: 250px

    .error-line
      @apply .bg-red-700 .relative

  .pane-header
    @apply .bg-grey-900 .rounded
    @apply .pb-3 .pt-1 .-mb-2 .z-10

  // for now, let's just do this
  .logger
    max-height: 250px

</style>
