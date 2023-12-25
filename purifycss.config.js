const purify = require('purify-css');

let content = ['./src/templates/**/*.html', './src/static/js/**/*.js'];
let css = ['./src/static/css/style.css'];

let options = {
  output: './src/static/css/purified.css',
  minify: true,
  info: true,
  whitelist: ['dropdown-item', 'badge', 'ckeditor', 'nav-item', 'dropdown', 'dropdown-menu', 'show'] 
};

purify(content, css, options, function (purifiedResult) {
  console.log('PurifyCSS has completed.');
});
