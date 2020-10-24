<template>
  <div class="code-container ui-element w-full p-2">
    <AceEditor
      @init="editorInit"
      lang="python"
      theme="dracula"
      width="100%" height="200"
      v-model="value"
      />

      <!-- old editor
      <textarea class="container h-full border-box border-none resize-none"
        id="code"
        ></textarea>
      -->
    </div>

</template>

<script>
import AceEditor from 'vue2-ace-editor'

export default {
  name: 'CodeEditor',
  components: {
    AceEditor
  },
  data() {
    const defaultScript =`
for found in cell.scan():
    if type(found) is Nutrient:
        cell.set_destination(found.position)

if cell.size > 100:
   cell.divide()`

    return {
      value: defaultScript.trim(),
    }
  },
  methods: {
    editorInit() {
      require('brace/ext/language_tools')
      require('brace/mode/python')                
      require('brace/theme/dracula')
    }
  }
}
</script>

<style lang="sass">

</style>
