django.jQuery(document).ready(function() {
    var calculate_length = function(input) {
        var checker = input.parent().find('.test-length');
        var max_length = parseInt(input.attr('maxlength'));
        checker.text(max_length - input.val().length);
    };

    django.jQuery('fieldset.meta-descriptions span.test-length').each(function() {
        var input = $(this).parents('div.field-box').find('input');
        calculate_length(input);
    });

    django.jQuery('fieldset.meta-descriptions input[id^="id_meta_summary_"]').on('input propertychange paste', function(e) {
        var input = django.jQuery(e.target);
        calculate_length(input);
    });
    django.jQuery('fieldset.meta-descriptions input[id^="id_twitter_summary_"]').on('input propertychange paste', function(e) {
        var input = django.jQuery(e.target);
        calculate_length(input);
    });

    django.jQuery('.mce-menu-item-glyphicon-ok .mce-text').text('foobar1');
});

/**
 * TinyMCE setup function.
 */
var tinymce_setup = function(editor) {
    /** 
     * Extend the passed object with another object, similar to Python's dict.update().
     *
     * This function is copied from TinyMCE (src/core/src/main/js/util/Tools.js).
     */
    var extend = function(obj, ext) {
      var i, l, name, args = arguments, value;

      for (i = 1, l = args.length; i < l; i++) {
        ext = args[i];
        for (name in ext) {
          if (ext.hasOwnProperty(name)) {
            value = ext[name];

            if (value !== undefined) {
              obj[name] = value;
            }
          }
        }
      }

      return obj;
    };

    /** Buttons for the table menu */
    ['tablestriped', 'tablebordered', 'tablecondensed', 'tablehover'].forEach(function(cls) {
        name = cls.substr(5);
        name = name.charAt(0).toUpperCase() + name.slice(1);
        editor.addButton(cls, {
            text: name,
            onclick: function() {
                editor.execCommand('mceToggleFormat', false, cls);
            },
            onpostrender: function() {
                /** 
                 * Note: This is supposed to activate the button when the style is active (e.g.
                 * like th bold button when you're in bold text), but it only works in the main
                 * toolbar.
                 */
                
                var btn = this;
                editor.on('init', function() {
                    editor.formatter.formatChanged(cls, function(state) {
                        btn.active(state);
                    });
                });
            }
        });
    });

    var glyphs = [
        'download',
        'envelope',
        'exclamation-sign',
        'file', 
        'home', 
        'minus',
        'ok',
        'pencil',
        'plus', 
        'refresh',
        'remove',
        'repeat',
        'zoom-in',
        'zoom-out', 
    ];
    /**
     * Glyphicons
     */
    editor.addButton('glyphs', {
        type: 'listbox',
        text: 'Glyphs',
        icon: false,
        onselect: function (e) {
            /**
             * NOTE: We append a zero-width space at the end of the span because otherwise adding a
             * Glyph in an empty paragraph eates the next element.
             */
            var val = this.value();
            editor.insertContent(
                '<span class="glyphicon glyphicon-' + val + '" aria-hidden="true"></span>&#x200b;'
            );
        },
        onclick: function(e) {
            $('.mce-menu-item-glyphicon').each(function() {
                var elem = $(this);
                var glyph_cls = elem.attr('class').split(/\s+/).filter(function(e) {
                    return e.startsWith('mce-menu-item-glyphicon-');
                })[0];
                glyph = glyph_cls.substr(24);
                console.log(glyph_cls);
                $('.' + glyph_cls + ' .mce-ico').replaceWith(
                    '<span class="glyphicon glyphicon-' + glyph + '"></span>');
            });
        },
        values: function() {
            var vals = [];
            glyphs.forEach(function(glyph) {
                var text = glyph.replace(/-/, ' ');
                var text = text.replace(/\w\S*/g, function(txt) {  // capitalize words
                    return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
                });
                vals.push({
                    text: text,
                    value: glyph,
                    classes: 'menu-item-glyphicon menu-item-glyphicon-' + glyph
                });
            });
            return vals;
        }(),
        onPostRender: function () {
            var button = this;
            editor.on('NodeChange', function(e) {
                // Make sure that the listbuton name is always the same
                button.value('Glyphs');
            });
            return;
        }
    });

    /** The lables list box */
    editor.addButton('labels', {
        type: 'listbox',
        text: 'Labels',
        icon: false,
        onselect: function (e) {
            var val = this.value();
            if (val == 'Labels') {
                return;
            }

            if (tinymce.activeEditor.formatter.match(val)) {
                // format is already applied, so remove it
                tinymce.activeEditor.formatter.remove(val);
            } else {
                tinymce.activeEditor.formatter.remove('label_default');
                tinymce.activeEditor.formatter.remove('label_primary');
                tinymce.activeEditor.formatter.remove('label_success');
                tinymce.activeEditor.formatter.remove('label_info');
                tinymce.activeEditor.formatter.remove('label_warning');
                tinymce.activeEditor.formatter.remove('label_danger');
                tinymce.activeEditor.formatter.apply(val);
            }
        },
        values: [
            {text: 'Default', value: 'label_default' },
            {text: 'Primary', value: 'label_primary', 'classes': 'label label-primary',
             format: 'label_primary'
            },
            {text: 'Success', value: 'label_success', 'classes': 'label label-success',
             format: {name: 'label_success'}
            },
            {text: 'Info', value: 'label_info', 'classes': 'label label-info',
             style: 'font-weight: 200'
            },
            {text: 'Warning', value: 'label_warning', 'classes': 'label label-warning'},
            {text: 'Danger', value: 'label_danger', 'classes': 'label label-danger'},
        ],
        onpostrender: function() {
            var button = this;

            editor.on('NodeChange', function(e) {
                if (! tinymce.activeEditor.formatter) {
                    return;
                }

                var matched = tinymce.activeEditor.formatter.matchAll(
                        ['label_default', 'label_primary', 'label_success', 'label_info',
                         'label_warning', 'label_danger'])
                if (matched.length == 0) {
                    button.value('Labels');
                } else {
                    button.value(matched[0]);
                }
            });
        }
    });

    editor.addButton('tooltips', {
        text: 'Tooltips',
        icon: false,
        stateSelector: 'span.footnote',
        onclick: function() {
            var data = {};
            var selection = editor.selection;

            /**
             * This is more or less copied from the TinyMCE source code:
             * src/plugins/link/src/main/js/Plugin.js, where the link plugin is defined.
             *
             * Essentially we define a "data" object and populate it with tooltip and text from the
             * current selection. The object is passed to editor.windowManager.open() to populate 
             * the form fields defined in the "body" property.
             */
            selectedElm = selection.getNode();
            anchorElm = editor.dom.getParent(selectedElm, 'span.footnote');
            data.text = initialText = anchorElm ? (anchorElm.innerText || anchorElm.textContent) : selection.getContent({ format: 'text' });
            data.tooltip = anchorElm ? editor.dom.getAttrib(anchorElm, 'title') : '';

            editor.windowManager.open({
                title: 'Tooltip',
                body: [
                  {type: 'textbox', name: 'tooltip', label: 'Tooltip',
                   onchange: function() {  /* Update the data dict on any change */
                       data.tooltip = this.value();
                   }
                  },
                  {type: 'textbox', name: 'text', label: 'Text', 
                   onchange: function() {  /* Update the data dict on any change */
                       data.text = this.value();
                   }
                  }
                ],
                data: data,  /* Sets the initial values of the body elements */
                onsubmit: function(e) {
                    var createTooltip = function() {
                        /* if anchorElm is defined, we are already in a tooltip and need to update it */
                        if (anchorElm) {
                            editor.focus();

                            if (data.text != initialText) {
                                if ("innerText" in anchorElm) {
                                    anchorElm.innerText = data.text;
                                } else {
                                    anchorElm.textContent = data.text;
                                }
                            }
                            console.log(data);
                            editor.dom.setAttribs(anchorElm, {title: data.tooltip});

                            /* No idea what this does, but present in link plugin: */
                            selection.select(anchorElm);
                            editor.undoManager.add();
                        } else {  /* new tooltip */
                            /**
                             * The title may contain HTML (e.g. links), so the text needs to be properly
                             * encoded.  There seems to be no real Javascript function for this, so we create
                             * that using jQuery.
                             */
                            var span = $('<span class="footnote" data-toggle="tooltip"></span>');
                            span.attr('title', tooltip);
                            span.text(data.text);
                            editor.insertContent(span[0].outerHTML);
                        }
                    }

                    var insertTooltip = function() {
                        editor.undoManager.transact(createTooltip);
                    }

                    data = extend(data, e.data);

                    var tooltip = data.tooltip;
                    if (!tooltip) {
                        /* TODO: Remove tooltip */
                        return;
                    }

                    insertTooltip();
                }
            });
        }
    });
};
