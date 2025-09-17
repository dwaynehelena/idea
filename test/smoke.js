const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const PORT = 8123;
const ROOT = path.join(__dirname, '..', 'dist');

function serveOnce() {
  const server = http.createServer((req, res) => {
    let filePath = path.join(ROOT, req.url === '/' ? '/index.html' : req.url);
    fs.readFile(filePath, (err, data) => {
      if(err){ res.statusCode=404; res.end('not found'); }
      else { res.end(data); }
    });
  });
  return new Promise((resolve)=> server.listen(PORT, ()=>resolve(server)));
}

(async ()=>{
  const server = await serveOnce();
  console.log('server started on', PORT);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  try{
    await page.goto(`http://127.0.0.1:${PORT}/` , { waitUntil: 'domcontentloaded' });
    // wait a moment for bundle to execute
    await page.waitForTimeout(500);
    const exists = await page.evaluate(() => !!(window.Galaga3D || window.default || window.galaga));
    console.log('Galaga3D constructor exists:', exists);
    await browser.close();
    server.close();
    process.exit(exists?0:2);
  }catch(e){
    console.error(e);
    await browser.close();
    server.close();
    process.exit(3);
  }
})();
