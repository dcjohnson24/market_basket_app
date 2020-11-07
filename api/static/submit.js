function showDiv(className) {
    document.getElementsByClassName(className)[0].style.display = 'block'; 
}

function post(path, params, method='post') {
    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    const form = document.createElement('form');
    form.method = method;
    form.action = path;

    for (const key in params) {
        if (params.hasOwnProperty(key)) {
            const hiddenField = document.createElement('input');
            hiddenField.type = 'hidden';
            hiddenField.name = key;
            hiddenField.value = params[key];

            form.appendChild(hiddenField);
        }
    }
    document.body.appendChild(form);
    form.submit();
}
window.addEventListener('load', () => {
    document.getElementById('btn_table').addEventListener('click', () => {
        showDiv('loading');
        post(
            display_association_rules, 
            {'metric': document.getElementById('metric').value}
        );
    });
    document.getElementById('btn_heatmap').addEventListener('click', () => {
        showDiv('loading');
        post(
            plot_heatmap,
            {'metric' : document.getElementById('metric').value}
        );
    });
    document.getElementById('btn_graph').addEventListener('click', () => {
        showDiv('loading');
        post(
            plot_network_graph,
            {'metric': document.getElementById('metric').value}
        );
    });
});