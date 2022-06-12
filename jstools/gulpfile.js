var gulp = require('gulp');
var uglify = require('gulp-uglify');
var rename = require("gulp-rename");;

gulp.task('compactJS', function () { 
    return new Promise(function(resolve, reject) {
        console.log("compactJS");
        resolve();
    });
});

gulp.task('js', function () {
    return gulp
      .src('./js/*.js') // ไฟล์ที่ต้องการ uglify() //./src/admin/main.js  ../static/js/*.js
      .pipe(uglify()) // สั่ง execute uglify() 
      .pipe(rename({ suffix: '.min' })) // เพิ่ม .min ต่อท้ายไฟล์
      .pipe(gulp.dest('../static/js')) // โฟลเดอร์ที่ต้องการเซฟ //../static/js/
});
  
gulp.task('watch', function() {
      gulp.watch('./js/*.js', gulp.series('js'));
});
  
//gulp.task('default', ['watch']);
//gulp.task('all', ['js', 'watch']);

gulp.task('default', gulp.series('js', 'watch'));