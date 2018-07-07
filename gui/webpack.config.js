const path=require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const ExtractTextPlugin = require("extract-text-webpack-plugin");
var isProduction=(process.env.NODE_ENV === 'production') || (process.argv.indexOf('-p') !== -1);

let outdir="debug";
if (isProduction) {
    outdir="release";
}
let devtool="inline-source-map";
let resolveAlias={};
if (isProduction) {
    devtool="";
    resolveAlias['react$']=__dirname+"/node_modules/react/cjs/react.production.min.js";
    resolveAlias['react-dom$']=__dirname+"/node_modules/react-dom/cjs/react-dom.production.min.js";
}
module.exports = function(env) {
    return {
        context: path.join(__dirname, 'src'),
        entry: [
            './index.js',
        ],
        output: {
            path: ((env && env.outpath) ? path.join(env.outpath,outdir) : path.join(__dirname, 'build',outdir)),
            filename: 'bundle.js',
        },
        module: {
            rules: [
                {
                    test: /\.js$/,
                    exclude: /node_modules/,
                    use: [
                        'babel-loader',
                    ],
                },
                {
                    test: /node_modules.react-toolbox.*\.css$/,
                    use: [
                        "style-loader",
                        {
                            loader: "css-loader",
                            options: {
                                modules: true, // default is false
                                sourceMap: true,
                                importLoaders: 1,
                                localIdentName: "[name]--[local]--[hash:base64:8]"
                            }
                        },
                        {
                            loader: 'postcss-loader',
                            options: {
                                config: {},
                                ident: 'postcss',
                                plugins: (loader) =>[
                                    require('postcss-cssnext')()
                                ]
                            }
                        }
                    ]
                },

                {
                    test: /\.css$/,
                    exclude: /node_modules.react-toolbox/,
                    use: ExtractTextPlugin.extract({fallback: 'style-loader', use: 'css-loader'})
                },

                {
                    test: /\.less$/,
                    exclude: /theme..*less/,
                    use: ExtractTextPlugin.extract({fallback: "style-loader", use: "css-loader?-url!less-loader"})
                },
                {
                    test: /theme.*\.less$/,
                    use: ["style-loader",
                        {
                            loader: "css-loader",
                            options: {
                                modules: true, // default is false
                                sourceMap: true,
                                importLoaders: 1,
                                localIdentName: "[name]--[local]--[hash:base64:8]"
                            }
                        },
                        'less-loader'

                    ]
                },

            ]
        },
        resolve: {
            alias: resolveAlias,
            modules: [
                path.join(__dirname, 'node_modules'),
            ],
        },
        plugins: [
            new CopyWebpackPlugin([
                // {output}/file.txt
                {from: '../public'}

            ]),
            new ExtractTextPlugin("index.css", {allChunks: true}),
        ],
        devtool: devtool
    }
};
