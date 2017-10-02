var fs = require("fs");
var jsdom = require("jsdom")
var readability = require("./readability/index");
var Readability = readability.Readability;
var JSDOMParser = readability.JSDOMParser;

var args = process.argv.slice(2);

input_path = args[0];
output_path = args[1];

// Read input file and construct a DOM Document object
// Works with emopty file
// TODO: Wrap in try/catch to handle missing file
original_page = fs.readFileSync(input_path, "utf-8");
document = new jsdom.JSDOM(original_page).window.document;

// Generate fake URI as one is required by Readability
var uri = {
        spec: "http://fakehost/test/page.html",
        host: "fakehost",
        prePath: "http://fakehost",
        scheme: "http",
        pathBase: "http://fakehost/test/"
      };
// Try and extract a readable article from the page contents
try {
  var reader = new Readability(uri, document, {debug: false});
  article = reader.parse();
}
catch(e) {
  console.log("Could not make page readable (error thrown on readability parsing)")
  return 1
}
// If readable article extracted, get the content
if(article != null) {
  readable_page = article.content;
}
else {
  console.log("Could not make page readable (no readable article generated)");
  return 1
}
// Write article content to disk
fs.writeFile(output_path, readable_page, function(err) {
  if(err) {
    console.log("Could not save readable page.");
    return 1
  }
  console.log("Saved readable page to " + output_path);
  return 0
});
