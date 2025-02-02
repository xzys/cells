const webpack = require("webpack");
const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const CopyPlugin = require('copy-webpack-plugin');
const VueLoaderPlugin = require('vue-loader/lib/plugin')

module.exports = {
  mode: "development",
  output: {
    chunkFilename: '[name].bundle.js',
    filename: '[name].bundle.js',
    path: path.resolve(__dirname, '../', 'dist'),
  },
  devtool: "eval-source-map",
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules|pyodide|.*\.py/,
        use: {
          loader: "babel-loader"
        }
      },
      {
        test: /\.s[ac]ss$/i,
        use: ['style-loader', 'css-loader', 'sass-loader']
      },
      /* // not working right now, debug later
      {
        test: /\.s[ac]ss$/i,
        use: [
          'vue-style-loader',
          'css-loader',
          {
            loader: 'sass-loader',
            options: {
              sassOptions: {
                indentedSyntax: true
              }
            }
          }
        ]
      },
      */
      {
        test: /\.vue$/,
        loader: 'vue-loader'
      },
      {
        test: [/\.vert$/, /\.frag$/],
        use: "raw-loader"
      },
      {
        test: /\.(gif|png|jpe?g|svg|xml)$/i,
        use: "file-loader"
      },
    ]
  },
  plugins: [
    new VueLoaderPlugin(),
    new webpack.DefinePlugin({
      CANVAS_RENDERER: JSON.stringify(true),
      WEBGL_RENDERER: JSON.stringify(true)
    }),
    new HtmlWebpackPlugin({
      template: "./index.html"
    }),
    new CopyPlugin({
      patterns: [
        {
          from: '../pyodide',
          to: 'pyodide',
          filter: path => !!path.match(/pyodide\/pyodide\.*/),
        },
        {
          from: '../simulation',
          to: 'simulation',
          filter: path => !!path.match(/.*\.py$/),
        }
      ]
    })
  ]
};
