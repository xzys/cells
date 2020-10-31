const webpack = require("webpack")
const path = require("path")
const fs = require('fs')

const HtmlWebpackPlugin = require("html-webpack-plugin")
const CopyPlugin = require('copy-webpack-plugin')


function readDirRecursive(dir, extensions, subdir = '', files = []) {
  fs.readdirSync(dir).forEach(file => {
    const abs = path.join(dir, file)
    const rel = path.join(subdir, file)

    if (fs.statSync(abs).isDirectory()) {
      return readDirRecursive(abs, extensions, subdir+file, files)
    } else if (extensions.some(ext => abs.endsWith(`.${ext}`))) {
      return files.push(rel)
    }
  })
  return files
}

module.exports = {
  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        CANVAS_RENDERER: JSON.stringify(true),
        WEBGL_RENDERER: JSON.stringify(true),
        // inject python files needed for simulation
        SIM_LIB_FILES: webpack.DefinePlugin.runtimeValue(
          () => JSON.stringify(
            readDirRecursive('../simulation', ['py'])
              .filter(fn => fn !== 'main.py')
          ),
          true
        ),
      }),
      new HtmlWebpackPlugin({ template: "./index.html" }),
      new CopyPlugin({
        patterns: [
          {
            from: './pyodide',
            to: 'pyodide',
            filter: path => (
              !!path.match(/pyodide\/pyodide\.*/) || 
              !!path.match(/pyodide\/packages\.json/)
            ),
          },
          {
            from: '../simulation',
            to: 'simulation',
            filter: path => !!path.match(/.*\.py$/),
          }
        ]
      })
    ],
  },
  chainWebpack: config => {
    config.module
      .rule('js')
      .exclude
        .add('/pyodide/')
        .end()

    const svgRule = config.module.rule('svg')
    svgRule.uses.clear()
    svgRule
      .use('vue-loader')
        .loader('vue-loader')
        .end()
      .use('vue-svg-loader')
        .loader('vue-svg-loader');
  }
}
