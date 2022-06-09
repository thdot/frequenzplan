function format_child(d)
{
    return (`
        <table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">
          <tr><td>Frequenzteilplan:</td><td>${d.Frequenzteilplan}</td></tr>
          <tr><td>Eintrag:</td><td>${d.Eintrag}</td></tr>
          <tr><td>Frequenzbereich:</td><td>${d.Frequenzbereich}</td></tr>
          <tr><td>Nutzungsbestimmung(en):</td><td>${d.Nutzungsbestimmungen}</td></tr>
          <tr><td>Funkdienst:</td><td>${d.Funkdienst}</td></tr>
          <tr><td>Nutzung:</td><td>${d.Nutzung}</td></tr>
          <tr><td>Frequenznutzung:</td><td>${d.Frequenznutzung}</td></tr>
          <tr><td>Frequenzteilbereich(e):</td><td>${d.Frequenzteilbereiche}</td></tr>
          <tr><td>Frequenznutzungsbedingungen:</td><td><pre>${d.Frequenznutzungsbedingungen}</pre></td></tr>
        </table>`);
}

var dataSet;

function loadData(url)
{
	var json = null;
	$.ajax({
		'async': false,
		'global': false,
		'url': url,
		'dataType': 'json',
		'success': function(data) {
			json = data;
		}
	});
	return json;
}

function init_tippy()
{
    $.each(dataSet.terms_of_use, function (id, term) {
        tippy(`.term_${id}`, {
            content: `<pre>${term}</pre>`,
            allowHTML: true,
            maxWidth: '750px',
        });
    });
}

$(document).ready(function ()
{
    dataSet = loadData('data.json');

    var table = $('#frequenzplan').DataTable({
        data: dataSet.entries,
        select:'single',
        columns: [
            {
              className: 'details-control',
              orderable: false,
              data: null,
              defaultContent: '',
              render: () => '<i class="fa fa-plus-square" aria-hidden="true"></i>',
              width: '15px'
            },
            { data: 'Frequenzteilplan', visible: false },
            { data: 'Eintrag', visible: false },
            { data: 'Frequenzbereich' },
            { data: 'Frequenzteilbereiche' },
            { data: 'Funkdienst' },
            { data: 'Nutzung' },            {
              data: 'Nutzungsbestimmungen',
              render: function (data, type, row) {
                  terms = ''
                  $.each( data.split(' '), function (_, id) {
                    terms += `<u class="term_${id}">${id}</u> `;
                  });
                  return terms;
              }
            },
            { data: 'Frequenznutzung' },
            {
              data: 'Frequenznutzungsbedingungen',
              render: function (data, type, row) {
                  l = data.split('\n')
                  return l[0] + (l[1] ? ' ...' : '')
              }
            },
            { data: 'Frequenznutzungsbedingungen', visible: false },
        ],
        order: [],
        initComplete: init_tippy,
        drawCallback: init_tippy,
    });

    // Add event listener for opening and closing details
    $('#frequenzplan tbody').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var tdi = tr.find('i.fa');
        var row = table.row(tr);

        if (row.child.isShown()) {
            row.child.hide();
            tr.removeClass('shown');
            tdi.first().removeClass('fa-minus-square');
            tdi.first().addClass('fa-plus-square');
        } else {
            row.child(format_child(row.data())).show();
            tr.addClass('shown');
            tdi.first().removeClass('fa-plus-square');
            tdi.first().addClass('fa-minus-square');
        }
    });

    table.on('user-select', function (e, dt, type, cell, originalEvent) {
        if ($(cell.node()).hasClass('details-control')) {
            e.preventDefault();
        }
    });
});
