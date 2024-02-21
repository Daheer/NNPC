/*
 * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 * See LICENSE in the project root for license information.
 */

/* global document, Office, Word */

Office.onReady((info) => {
  if (info.host === Office.HostType.Word) {
    // Assign event handlers and other initialization logic.
    document.getElementById("insert-paragraph").onclick = () => tryCatch(insertParagraph);
    document.getElementById("sideload-msg").style.display = "none";
    document.getElementById("app-body").style.display = "flex";
    //document.getElementById("run").onclick = run;
  }
});

async function insertParagraph() {
  await Word.run(async (context) => {

    const docBody = context.document.body;
    const docContent = context.document.body;
    context.load(docBody, 'text');
    await context.sync();

    console.log(docBody.text);
    const response = document.getElementById("response");
    const header = document.getElementById("header");
    response.innerHTML = '';
    header.innerHTML = 'Loading...';

    await fetch('https://da5e-34-66-174-126.ngrok-free.app/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: docBody.text }),
    })
      .then(response => response.json())
      .then(data => {
        console.log(data);
        header.innerHTML = 'Summary';
        response.innerHTML = data.summary;
      })
      .catch(error => {
        console.error('Error:', error);
      });
  });
}

/** Default helper for invoking an action and handling errors. */
async function tryCatch(callback) {
  try {
    await callback();
  } catch (error) {
    // Note: In a production add-in, you'd want to notify the user through your add-in's UI.
    console.error(error);
  }
}

/**export async function run() {
  return Word.run(async (context) => {
    /**
     * Insert your Word code here
     */

// insert a paragraph at the end of the document.
/*const paragraph = context.document.body.insertParagraph("Hello World", Word.InsertLocation.end);

// change the paragraph color to blue.
paragraph.font.color = "blue";

await context.sync();
});
}*/

