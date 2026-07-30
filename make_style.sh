#!/bin/sh
cd "$(dirname "$0")" || exit

node scripts/check-package-installed.js postcss sass autoprefixer || exit

build_style() {
  echo "Creating $1 style..."
  cp resources/vars-$1.scss resources/vars.scss
  npx sass resources:sass_processed
  npx postcss \
      sass_processed/ace-dmoj.css \
      sass_processed/featherlight.css \
      sass_processed/martor-description.css \
      sass_processed/select2-dmoj.css \
      sass_processed/style.css \
      sass_processed/blog-modern.css \
      sass_processed/blog-post.css \
      sass_processed/theme-toggle.css \
      sass_processed/ui_form.css \
      sass_processed/task_status.css \
      sass_processed/source_sans_pro.css \
      --verbose --use autoprefixer -d "$2"
  rm resources/vars.scss
}

build_style 'default' 'resources'

echo "Compiling notification.scss..."
npx sass resources/notification.scss resources/notification.css --no-source-map
npx postcss resources/notification.css --verbose --use autoprefixer -o resources/notification.css
