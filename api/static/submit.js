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
    if (location.pathname.includes('completed')) {

        document.getElementsByClassName('selection')[0]
            .getElementsByTagName('input')[0]
            .addEventListener('click', event => {
                ['table', 'graph', 'heatmap'].map(showDiv);
                event.preventDefault(); // Prevent form from submitting.
            }); 


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
    } else if (location.pathname == '/') {
        document.getElementById('btn_demo').addEventListener('click', () => {
            location.assign(demo_page);
        });
    } else if (location.pathname.includes('demo_selection')) {
        document.getElementsByClassName('selection')[0]
        .getElementsByTagName('input')[0]
        .addEventListener('click', event => {
            event.preventDefault();
            post(
                view_demo,
                {'metric': document.getElementById('metric').value}
            );
        }); 
    };
}); 
