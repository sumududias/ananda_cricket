$(document).ready(function() {
    // Initialize Select2 for all searchable dropdowns
    $('.searchable-dropdown').each(function() {
        var $select = $(this);
        var searchUrl = $select.data('search-url');
        
        $select.select2({
            theme: 'bootstrap4',
            placeholder: 'Search...',
            allowClear: true,
            minimumInputLength: 0,
            ajax: {
                url: searchUrl,
                dataType: 'json',
                delay: 250,
                data: function(params) {
                    return {
                        q: params.term || '',
                        page: params.page || 1
                    };
                },
                processResults: function(data, params) {
                    return {
                        results: data.results,
                        pagination: {
                            more: false
                        }
                    };
                },
                cache: true
            }
        });
    });

    // Add new option modal functionality
    $('.add-option-btn').click(function() {
        var optionType = $(this).data('option-type');
        var targetField = $(this).data('target-field');
        
        $('#addOptionModal').find('#option-type').val(optionType);
        $('#addOptionModal').find('#target-field').val(targetField);
        $('#addOptionModal').modal('show');
    });

    // Submit new option via AJAX
    $('#add-option-form').submit(function(e) {
        e.preventDefault();
        
        var formData = {
            'option_type': $('#option-type').val(),
            'value': $('#option-value').val(),
            'display': $('#option-display').val(),
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
        };
        
        $.ajax({
            type: 'POST',
            url: '/cricket/add-dropdown-option/',
            data: formData,
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    // Create new option and add to select
                    var targetField = $('#target-field').val();
                    var newOption = new Option(response.text, response.id, true, true);
                    $('#' + targetField).append(newOption).trigger('change');
                    
                    // Close modal and reset form
                    $('#addOptionModal').modal('hide');
                    $('#add-option-form')[0].reset();
                    
                    // Show success message
                    showAlert('success', response.message);
                } else {
                    showAlert('danger', response.message);
                }
            },
            error: function(xhr, status, error) {
                showAlert('danger', 'An error occurred: ' + error);
            }
        });
    });

    // Helper function to show alerts
    function showAlert(type, message) {
        var alertHtml = '<div class="alert alert-' + type + ' alert-dismissible fade show" role="alert">' +
                        message +
                        '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                        '<span aria-hidden="true">&times;</span></button></div>';
        
        $('#alert-container').html(alertHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            $('.alert').alert('close');
        }, 5000);
    }
});
