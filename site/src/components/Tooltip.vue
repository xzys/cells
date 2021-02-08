<template>
  <div class="tooltip-box">
    <a href="#">{{ hoverText }}</a>
    <div class="tooltip">
      <span class="triangle"></span>
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    active: {
      type: Boolean,
      default: false,
    },
    hoverText: {
      type: String,
      default: 
    },
  }
}
</script>
<style lang=sass">

.tooltip-box
  position: relative

  .tooltip
    width: 200px;
    background: #000000;
    color: #ffffff;
    text-align: center;
    padding: 10px 20px 10px 20px;
    border-radius: 5px;
    top: 50%;
    left: calc(100% + 11px);
    transform: translate-y(-50%)

  .triangle
    border-width: 0 6px 6px;
    border-color: transparent;
    border-bottom-color: #000000;
    position: absolute;
    left: -6px;
    top: calc(50% - 3px);
    transform: rotate(270deg) translate-y(-50%)

</style>
