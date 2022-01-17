const webpack = require('webpack');

module.exports = {
    webpack: function(config, env) {

        config.resolve.fallback = {
            Buffer: require.resolve('buffer/'),
            process: require.resolve('process/')
        }
        config.plugins.push(
            new webpack.ProvidePlugin({
                Buffer: ['buffer', 'Buffer'],
                process: ['process']
            })
        )

        console.log(config)

        return config
    }
}
