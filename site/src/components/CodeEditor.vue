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
        @click="saveScript">
        <IconRefresh class="icon"/>
      </div>
      <div class="button-icon button-inactive">
        <IconHand class="icon"/>
      </div>
    </div>

    <div class="code-container w-full flex-1">
      <div class="editor-container ui-element p-2 z-20 relative resize-y">
        <AceEditor
          @init="editorInit"
          lang="python"
          theme="dracula"
          width="100%" height="100%"
          v-model="value"
          />
      </div>
      <Logger
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

export default {
  name: 'CodeEditor',
  components: {
    AceEditor, Logger,
    IconPlay, IconPause, IconRefresh, IconHand,
  },
  data() {
    const defaultScript = (`
print('my pos', cell.position)
for found in cell.scan():
    if type(found) is Nutrient:
        cell.set_destination(found.position)

if cell.size > 100:
   cell.divide()`).trim()

    return {
      lastValue: defaultScript,
      value: defaultScript,

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
    eventService.bus.on(eventService.events.ON_READY, self.saveScript)
  },
  methods: {
    editorInit() {
      require('brace/ext/language_tools')
      require('brace/mode/python')                
      require('brace/theme/dracula')
    },
    saveScript() {
      let self = this
      eventService.bus.emit(eventService.events.MODIFY_SCRIPT, self.value)
      self.lastValue = self.value
    },
    onPlayPause() {
      let self = this
      self.paused = !self.paused
    },
  }
}
</script>

<style lang="sass">

.editor-container
  height: 50%

</style>
