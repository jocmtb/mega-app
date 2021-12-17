// webpack.mix.js

let mix = require('laravel-mix');

mix
// .webpackConfig({
//     resolve: {
//         symlinks: false
//     },
    // plugins: [
    //     new BundleAnalyzerPlugin({
    //         analyzerMode: 'static'
    //     }),
    // ],
    // optimization: {
    //   splitChunks: {
    //     cacheGroups: {
    //       commons: {
    //         test: /[\\/]node_modules[\\/]/,
    //         name: 'vendors',
    //         chunks: 'all'
    //       }
    //     }
    //   }
    // }
// })
.setPublicPath('static')
.js('src/MWChecks.js', 'js')
.minify('static/js/MWChecks.js')
.disableNotifications();