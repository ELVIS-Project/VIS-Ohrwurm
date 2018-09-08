import { Component, OnInit, ViewChild } from '@angular/core';
import { VerovioHumdrumService } from '../verovio.service.ts';
import { AceEditorComponent } from 'ng2-ace-editor';

import defaultHumdrumInput from './default-input.ts';

@Component({
  selector: 'app-music-editor',
  templateUrl: './music-editor.component.html',
  styleUrls: ['./music-editor.component.css']
})
export class MusicEditorComponent implements OnInit {

  @ViewChild('editor') editor;
  @ViewChild('renderedHumdrum') renderedHumdrumDiv;

  humdrumInput: string = defaultHumdrumInput;
  renderedHumdrum: string;
  aceOptions: any;

  constructor(private verovio: VerovioHumdrumService) { }

  ngAfterViewInit() {
    // Register on-change event listener for the editor
    this.editor.getEditor().on('change', (delta) => {
      this.renderHumdrum();
    });
  }

  renderHumdrum() { 
    this.renderedHumdrum = this.verovio.render(this.humdrumInput);
    
  }


}

    /*
Vue.component("verovio-humdrum-viewer", {
    data: function() {
        return {
            input: document.getElementById('default_krn').text,
            vrv_options: {
                inputFormat: "humdrum",
                adjustPageHeight: 1,
                pageHeight: 1000,
                pageWidth: 1000,
                scale: 60,
                font: "Leipzig"
            }
        }
    },
    props: ['targetWindowFilter', 'transpositionFilter', 'diatonicOccFilter'],
    methods: {
        update: function(newstr) {
            this.input = newstr
        },
        updateProp(eventName, value){
            console.log("update " + eventName + ": ")
            console.log(value)
            this.$emit(eventName, value)
        }
    },
    computed: {
        verovioOutput: function() {
            return vrvToolkit.renderData(this.input, this.vrv_options);
        }
    },
    mounted: function(){
        var onChange = this.update;
        var editorId = "editor";
        var editorDiv = document.getElementById(editorId);

        var editor = ace.edit(editorId, {
            autoScrollEditorIntoView: true,
            value: this.input,
            minLines: 10,
            maxLines: 10
        });
        editor.session.on('change', function(delta){
            onChange(editor.getValue())
        });

        var onPropChange = this.updateProp
        $("#targetWindowSlider").slider({
            range: true,
            min: 1,
            max: 15,
            values: [1, 1],
            slide: function(event, ui){
                onPropChange('targetWindowFilter', ui.values)
            }
        });

        $("#transpositionSlider").slider({
            range: true,
            min: -12,
            max: 12,
            values: [-12, 12],
            slide: function(event, ui){
                onPropChange('transpositionFilter', ui.values)
            }
        });

        $("#diatonicOccFilter").checkboxradio();
    },

    */
