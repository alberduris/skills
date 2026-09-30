// Run mermaid-to-excalidraw in headless Chrome: Mermaid on stdin, its skeleton elements as JSON on stdout.
// Pins mermaid@11.12.1: with the newest Mermaid, the converter no longer finds the nodes it looks for
// and draws every state diagram as an image.
import { chromium } from "playwright-core";

const CONVERTER = "https://esm.sh/@excalidraw/mermaid-to-excalidraw@2.2.2?deps=mermaid@11.12.1";

const source = await new Promise((resolve) => {
  let text = "";
  process.stdin.on("data", (chunk) => (text += chunk)).on("end", () => resolve(text));
});
const browser = await chromium.launch({ channel: "chrome", headless: true });
try {
  const page = await browser.newPage();
  // Console errors carry the reason of a fallback to an image, and sometimes the image itself.
  page.on("console", (m) => m.type() === "error" && process.stderr.write(`${m.text().slice(0, 200)}\n`));
  await page.goto("https://esm.sh/");
  const elements = await page.evaluate(async ([converter, source]) => {
    const { parseMermaidToExcalidraw } = await import(converter);
    return (await parseMermaidToExcalidraw(source)).elements;
  }, [CONVERTER, source]);
  process.stdout.write(JSON.stringify(elements));
} finally {
  await browser.close();
}
