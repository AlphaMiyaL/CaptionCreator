// endpoint to lambda function
const ENDPOINT = 'https://nawgtrnw4iphi2m4ao6at6m4re0kdpcw.lambda-url.us-west-1.on.aws/';
// 5MB
const SIZE_LIMIT = 5 * 1024 * 1024;
const DIMENSION_MIN = 80;
const DIMENSION_MAX = 10000;

window.onload = () => {
    // validates file type
    const isTypeValid = type => !type.startsWith('image/') || (type != 'image/png' && type != 'image/jpeg');

    const getFileField = () => document.getElementById('fileField');
    const getGenerateButton = () => document.getElementById('generateButton');
    const getMessage = () => document.getElementById('message');
    const getImage = () => document.getElementById('image');

    const disableInput = () => {
        getFileField().setAttribute('disabled', 'true');
        getGenerateButton().setAttribute('disabled', 'true');
    };

    const enableInput = () => {
        getFileField().removeAttribute('disabled');
        getGenerateButton().removeAttribute('disabled');
    };

    const clearMessage = () => {
        const message = getMessage();
        message.innerText = '';
    };

    const showError = text => {
        const message = getMessage();
        message.innerText = text;
        message.style.color = '#ff0000';

        enableInput();
    };

    const showMessage = text => {
        const message = getMessage();
        message.innerText = text;
        message.style.color = null;

        enableInput();
    };

    const toBase64 = file => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
    };

    const submitImage = image => {
        showMessage('Waiting for caption...');

        fetch(ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'text/plain'
            },
            body: image
        }).then(
            response => handleResponse(response),
            error => {
                showError('Error with communicating with backend. See web console for more details.');
                console.log(error);
            }
        );
    };

    const handleResponse = response => {
        const contentType = response.headers.get('content-type');
        if (contentType != 'text/plain') {
            showError('Unexpected response content type: ' + contentType);
            return;
        }

        // handle unexpected statusCode
        if (response.status != 200) {
            showError('Error, status code: ' + response.status + '. See web console for more details.');
            console.log(response);
        }

        response.text().then(
            text => handleText(text),
            error => {
                showError('Error parsing server response. See web console for more details.');
                console.log(error);
                console.log('Response: ', response);
                return;
            }
        );
    };

    const handleText = text => {
        showMessage(text);
        enableInput();
    };

    const displayPreview = file => {
        const fileUrl = URL.createObjectURL(file);
        const image = getImage();
        image.src = fileUrl;
        image.onload = () => URL.revokeObjectURL(fileUrl);
        image.style.visibility = 'visible';
    };

    const removePreview = () => {
        image.style.visibility = 'hidden';
        image.src = null;
    };

    // validate the file field, returning the file if valid, false otherwise
    const getFile = () => {
        const fileField = getFileField();

        const files = fileField.files;
        // handle no files
        if (files.length <= 0) {
            showError('Select a file to upload.');
            return false;
        }

        // handle more than one file, only possible if they edit html
        if (files.length > 1) {
            showError('Unsupported number of files.');
            return false;
        }

        const file = files[0];
        // validate file type
        if (isTypeValid(file.type)) {
            showError('Only png and jpeg images are currently supported.');
            return false;
        }

        // validate file size
        if (file.size > SIZE_LIMIT) {
            showError('File size over 5mb limit.');
            return false;
        }

        return file;
    };

    const showPreview = () => {
        const file = getFile();
        if (!file)
            return false;

        displayPreview(file);
        return true;
    };

    getFileField().onchange = e => {
        removePreview();
        // if invalid change, prevent it
        if (!showPreview())
            e.preventDefault();
    };
    
    getGenerateButton().onclick = e => {
        clearMessage();
        disableInput();

        const file = getFile();
        if (!file) {
            enableInput();
            return;
        }

        submitImage(file);
        showMessage('Preparing image...');
        toBase64(file).then(
            base64 => submitImage(base64),
            error => {
                showError('Error with preparing file for transfer. See web console for more details.');
                console.log(error);
            }
        );
    };

    showPreview();
};