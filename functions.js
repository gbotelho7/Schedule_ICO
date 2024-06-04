/**
 * Recebe os dados e confirma se estão de acordo com as configurações.
 * @param {Object} results - Os resultados dos dados analisados.
 * @param {number} index - O índice dos resultados.
 * @param {Object} e - O objeto de evento.
 * @param {HTMLElement} hiddenDiv - A div oculta.
 * @param {boolean} classroomsInput - Booleano indicando se os dados são para salas de aula.
 * @returns {void}
 */
function handleParsedData(results, index, e, hiddenDiv, classroomsInput) {
  let headersMatch = false;
  console.log(dictionary)
  if (classroomsInput) {
    const dataArray = [
      'Edifício', 'Nome sala', 'Capacidade Normal', 'Capacidade Exame', 'Nº características',
      'Anfiteatro aulas', 'Apoio técnico eventos', 'Arq 1', 'Arq 2', 'Arq 3', 'Arq 4', 'Arq 5',
      'Arq 6', 'Arq 9', 'BYOD (Bring Your Own Device)', 'Focus Group', 'Horário sala visível portal público',
      'Laboratório de Arquitectura de Computadores I', 'Laboratório de Arquitectura de Computadores II',
      'Laboratório de Bases de Engenharia', 'Laboratório de Electrónica', 'Laboratório de Informática',
      'Laboratório de Jornalismo', 'Laboratório de Redes de Computadores I', 'Laboratório de Redes de Computadores II',
      'Laboratório de Telecomunicações', 'Sala Aulas Mestrado', 'Sala Aulas Mestrado Plus', 'Sala NEE',
      'Sala Provas', 'Sala Reunião', 'Sala de Arquitectura', 'Sala de Aulas normal', 'videoconferencia', 'Átrio'
    ];
    headersMatch = dataArray.every((header) => results.meta.fields.includes(header.trim()));
  }
  else if (Object.keys(dictionary).length === 0 && !classroomsInput) {
    headersMatch = defaultHeadersArray.every((header) => results.meta.fields.includes(header.trim()));
  } else {
    headersMatch = Object.values(dictionary).every((header) =>
      results.meta.fields.some((field) =>
        field.trim().toLowerCase() === header.trim().toLowerCase()
      )
    );
  }


  const dateFormatsMatch = dateColumns.split(";").every((column) =>
    results.meta.fields.includes(column) &&
    results.data.every(row => (moment(row[column], dateFormat, true).isValid() || row[column] === ''))
  );

  const timeFormatsMatch = hourColumns.split(";").every((column) =>
    results.meta.fields.includes(column) &&
    results.data.every(row => (moment(row[column], hourFormat, true).isValid() || row[column] === ''))
  );

  if ((headersMatch && dateFormatsMatch && timeFormatsMatch) || (headersMatch && classroomsInput)) {
    if (hiddenDiv.style.display === "none") {
      hiddenDiv.style.display = "block"
    }
  } else {
    if (hiddenDiv.style.display === "block" && classroomsInput) {
      hiddenDiv.style.display = "none"
    }
    dynamicCriteriums.style.display = "none"
    heatmapContainer.innerHTML = ""
    chartContainer.innerHTML = ""
    lineChartContainer.innerHTML = ""
    downloadContainer.innerHTML = ""
    modifiableTabulator.innerHTML = ""
    heatmapFilter.innerHTML = ""
    h4Elements.forEach(element => {
      element.style.display = 'none';
    });
    if (modifiableTabulator.classList.contains('tabulator')) {
      modifiableTabulator.classList.remove('tabulator');
    }
    if (chartContainer.classList.contains('tabulator')) {
      chartContainer.classList.remove('tabulator');
    }
    for (let i = 0; i < graphs.length; i++) {
      graphs[i].innerHTML = ''
    }
    e.target.value = "";
    if (!headersMatch) {
      alert("Os cabeçalhos das configurações não correspondem aos do Ficheiro. Certifique-se de que o cabeçalho e o delimitador estão corretos. A tabela anterior será eliminada");
    } else if (!dateFormatsMatch) {
      alert("O formato da data das configurações não corresponde ao encontrado no Ficheiro. Insira as alterações necessárias. A tabela anterior será eliminada");
    } else if (!timeFormatsMatch) {
      alert("O formato de hora das configurações não corresponde ao encontrado no Ficheiro. Insira as alterações necessárias. A tabela anterior será eliminada");
    }
  }
};


/**
 * Faz a recepção dos dados no caso dos URLs.
 * @param {string[]} urls - Array de URLs dos dados a serem processados.
 * @param {Object} e - O objeto de evento.
 * @param {HTMLElement} hiddenDiv - A div oculta.
 * @param {HTMLElement[]} h4Elements - Array de elementos h4.
 * @param {HTMLElement[]} graphs - Array de elementos gráficos.
 * @returns {void}
 */
function parseURLs(urls, e, hiddenDiv, h4Elements, graphs) {
  schedulesData = []
  urlsProcessed = 0
  errors = 0
  for (let i = 0; i < urls.length; i++) {
    const url = urls[i];
    Papa.parse(url, {
      download: true,
      delimiter: csvSeparator,
      header: true,
      error: function () {
        errors += 1
        urlsProcessed++;
        if (urls.length === errors) {
          alert("Nenhum dos urls submetidos é válido")
          dynamicCriteriums.style.display = "none"
          heatmapContainer.innerHTML = ""
          chartContainer.innerHTML = ""
          lineChartContainer.innerHTML = ""
          downloadContainer.innerHTML = ""
          modifiableTabulator.innerHTML = ""
          heatmapFilter.innerHTML = ""
          h4Elements.forEach(element => {
            element.style.display = 'none';
          });
          if (modifiableTabulator.classList.contains('tabulator')) {
            modifiableTabulator.classList.remove('tabulator');
          }
          if (chartContainer.classList.contains('tabulator')) {
            chartContainer.classList.remove('tabulator');
          }
          for (let i = 0; i < graphs.length; i++) {
            graphs[i].innerHTML = ''
          }
        }
        else {
          if (urlsProcessed === urls.length) {
            dynamicCriteriums.style.display = "block"
            schedulesData = orderSchedulesData(schedulesData)
            createTabulator(schedulesData, heatmapContainer, downloadContainer, modifiableTabulator, h4Elements, graphs)
            console.log("fiz tabulator")
            createLineChart(h4Elements)
          }
        }

      },
      complete: function (results) {
        const scheduleId = `Horário ${i + 1}`
        const scheduleData = { data: results.data };
        evaluateCriteriums(scheduleData)
        schedulesData[scheduleId] = scheduleData;
        console.log(schedulesData)
        handleParsedData(results, i, e, hiddenDiv, false);
        urlsProcessed++
        if (urlsProcessed === urls.length) {
          dynamicCriteriums.style.display = "block"
          schedulesData = orderSchedulesData(schedulesData)
          createTabulator(schedulesData, heatmapContainer, downloadContainer, modifiableTabulator, h4Elements, graphs)
          console.log("fiz tabulator")
          createLineChart(h4Elements)
        }
      }
    });
  }
  updateDynamicCriteriums(dropdown)
  populateOptions("formulaOptions", dynamicCriteriumsLists.formulaList);
  populateOptions("textOptions", dynamicCriteriumsLists.textList);
  saveSettings()
};


/**
 * Guarda as configurações e dados específicos no armazenamento local.
 * @returns {void}
 */
function saveSettings() {
  let settings = { "csvSeparator": csvSeparator, "hourFormat": hourFormat, "dateFormat": dateFormat, "dateColumns": dateColumns, "hourColumns": hourColumns, "dictionary": dictionary, "dynamicCriteriumsLists": dynamicCriteriumsLists }; //dictionary
  localStorage.setItem('executionData', JSON.stringify(settings));
  console.log(settings)
}


/**
 * Controla o comportamento dos switches tanto de inputs como de critérios.
 * @param {HTMLElement} input1 - O primeiro elemento input.
 * @param {HTMLElement} input2 - O segundo elemento input.
 * @param {HTMLElement} toggleSwitch - O switch para controle.
 * @param {HTMLElement} [fileInput] - O input de arquivo opcional.
 * @returns {void}
 */
function handleSwitch(input1, input2, toggleSwitch, fileInput) {
  if (toggleSwitch.checked) {
    input1.style.display = "none"
    input2.style.display = "block"
  } else {
    if (fileInput) {
      input1.style.display = ""
    } else {
      input1.style.display = "block"
    }

    input2.style.display = "none"
  }
}


/**
 * Adiciona novos inputs no caso de URLs.
 * @param {string} className - A classe dos inputs a serem adicionados.
 * @param {string} placeholderText - O texto do placeholder para os novos inputs.
 * @param {string} containerId - O ID do contêiner onde os novos inputs serão adicionados.
 * @returns {void}
 */
function addNewInput(className, placeholderText, containerId) {
  const inputs = document.querySelectorAll(`.${className}`);
  const lastInput = inputs[inputs.length - 1];

  if (lastInput && event.target === lastInput && lastInput.value.trim() !== '') {
    const newInput = document.createElement("input");
    newInput.type = "text";
    newInput.classList.add(className);
    newInput.placeholder = placeholderText;
    document.getElementById(containerId).appendChild(newInput);
  }
}


/**
 * Atualiza o valor de uma variável caso o elemento associado sofra alterações.
 * @param {string} elementId - O ID do elemento de entrada (input).
 * @param {string} variableToUpdate - O nome da variável a ser atualizada.
 * @returns {void}
 */
function handleInputChange(elementId, variableToUpdate) {
  const element = document.getElementById(elementId);
  if (element && element.value !== "") {
    window[variableToUpdate] = element.value;
  }
}


/**
 * Preenche os valores guardados como values dos inputs.
 * @param {string[]} listIds - Array de IDs dos elementos input.
 * @returns {void}
 */
function settingsToValue(listIds) {
  settings = [csvSeparator, hourFormat, dateFormat, hourColumns, dateColumns]
  for (let i = 0; i < listIds.length; i++) {
    if (i < settings.length) {
      document.getElementById(listIds[i]).value = settings[i]
    } else {
      document.getElementById(listIds[i]).value = dictionary[defaultHeadersArray[i - settings.length]]
    }
  }
}


/**
 * Recolhe os diferentes resultados dos critérios estáticos e coloca tudo dentro de um objeto.
 * @param {Object} results - Os resultados dos dados a serem avaliados pelos critérios.
 * @returns {Object} - O objeto contendo os resultados dos critérios estáticos.
 */
function evaluateCriteriums(results) {
  results = criteriumOvercrowding(results)
  results = criteriumOverlaping(results)
  results = criteriumClassRequisites(results)
}


/**
 * Avalia o critério de sobrelotação e conta o número de alunos em sobrelotação nos resultados fornecidos.
 * @param {Object} results - Os resultados dos dados a serem avaliados pelo critério de sobrelotação.
 * @returns {Object} - Os resultados atualizados com a contagem de sobrelotações e alunos a mais.
 */
function criteriumOvercrowding(results) {
  let countOvercrowding = 0
  let countTotalStudentsOvercrowding = 0
  for (let i = 0; i < results.data.length; i++) {
    let lotacao = results.data[i][dictionary['Lotação']]
    let inscritos = results.data[i][dictionary['Inscritos no turno']]
    if (lotacao - inscritos < 0) {
      countOvercrowding++
      countTotalStudentsOvercrowding += Math.abs(lotacao - inscritos)
      results.data[i]['Sobrelotações'] = true
    } else {
      results.data[i]['Sobrelotações'] = false
    }
  }
  let criteriumArray = {}
  criteriumArray['Sobrelotações'] = countOvercrowding
  criteriumArray['Alunos a mais (Sobrelotações)'] = countTotalStudentsOvercrowding;

  results['criteriums'] = criteriumArray
  return results
}


/**
 * Avalia o critério de sobreposição de aulas nos resultados fornecidos.
 * @param {Object} results - Os resultados dos dados a serem avaliados pelo critério de sobreposição de aulas.
 * @returns {Object} - Os resultados atualizados com a contagem de sobreposições.
 */
function criteriumOverlaping(results) {
  let classesByDate = {};

  for (let i = 0; i < results.data.length; i++) {
    if (!classesByDate[results.data[i][dictionary['Dia']]]) {
      classesByDate[results.data[i][dictionary['Dia']]] = [];
    }
    classesByDate[results.data[i][dictionary['Dia']]].push(results.data[i]);
  }
  let countOverlaping = 0
  console.log(classesByDate)
  if (classesByDate !== 1) {
    Object.keys(classesByDate).forEach((date) => {
      let classesForDate = classesByDate[date];
      for (let i = 0; i < classesForDate.length - 1; i++) {
        isTrue = false
        for (let j = i + 1; j < classesForDate.length; j++) {
          if ((classesForDate[i][dictionary['Início']] < classesForDate[j][dictionary['Fim']] && classesForDate[i][dictionary['Fim']] > classesForDate[j][dictionary['Início']]) ||
            (classesForDate[j][dictionary['Início']] < classesForDate[i][dictionary['Fim']] && classesForDate[j][dictionary['Fim']] > classesForDate[i][dictionary['Início']])) {
            countOverlaping++
            isTrue = true
          }
        }
        if (isTrue) {
          results.data[i]['Sobreposições'] = true
        } else {
          results.data[i]['Sobreposições'] = false
        }
      }
    });
  }
  results.criteriums['Sobreposições'] = countOverlaping
  return results
}


/**
 * Avalia o critério de requisitos de sala de aula e o número de aulas sem sala nos resultados fornecidos.
 * @param {Object} results - Os resultados dos dados a serem avaliados pelo critério de requisitos de sala de aula.
 * @returns {Object} - Os resultados atualizados com a contagem de requisitos não cumpridos e aulas sem sala.
 */

function criteriumClassRequisites(results) {
  let countRequisitesNotMet = 0
  let countNoClassroom = 0
  for (let i = 0; i < results.data.length; i++) {
    let askedRequisites = results.data[i][dictionary['Características da sala pedida para a aula']]
    let roomName = results.data[i][dictionary['Sala da aula']];
    if (roomName in classRoomDictionary) {
      if (!classRoomDictionary[roomName].includes(askedRequisites)) {
        countRequisitesNotMet++
        results.data[i]['Requisitos não cumpridos'] = true
        results.data[i]['Aulas Sem Sala'] = false
      } else {
        results.data[i]['Requisitos não cumpridos'] = false
        results.data[i]['Aulas Sem Sala'] = false
      }
    } else if (roomName === "" && askedRequisites != "Não necessita de sala") { //"
      countNoClassroom++
      results.data[i]['Requisitos não cumpridos'] = true
      results.data[i]['Aulas Sem Sala'] = true
    } else {
      results.data[i]['Requisitos não cumpridos'] = false
      results.data[i]['Aulas Sem Sala'] = false
    }
  }
  results.criteriums['Requisitos não cumpridos'] = countRequisitesNotMet
  results.criteriums['Aulas Sem Sala'] = countNoClassroom
  return results
}


/**
 * Avalia um critério de fórmula dinâmica nos dados fornecidos e atualiza os resultados com os resultados da avaliação.
 * @param {Object} schedulesData - Os dados dos horários a serem avaliados.
 * @param {string} expression - A expressão da fórmula a ser avaliada.
 * @returns {Object} - Os resultados atualizados com os resultados da avaliação da fórmula dinâmica.
 */
function evaluateDynamicFormulaCriterium(schedulesData, expression) {
  const foundColumnNames = extractColumnNamesFromExpression(expression, Object.values(dictionary)); // Utiliza os valores do cabeçalho recebido
  let errorCounter = 0
  Object.keys(schedulesData).forEach((scheduleId) => {
    let errorOccured = false
    const schedule = schedulesData[scheduleId];
    const scheduleData = schedule.data; // Assuming data is stored under 'data' property
    let counter = 0
    scheduleData.forEach((row, index) => {
      const rowSpecificExpression = substituteColumnNamesWithValues(expression, row, foundColumnNames);
      try {
        const result = math.evaluate(rowSpecificExpression);
        if (result) {
          counter++
          schedule.data[index][expression] = true;
        }
        else {
          schedule.data[index][expression] = false;
        }
      } catch (error) {
        console.error(`Error evaluating expression for row: ${error}`);
        errorOccured = true
        schedule.data[index][expression] = false;
      }
    });
    if (errorOccured) {
      errorCounter++
    } else {
      schedule.criteriums[expression] = counter;
    }
  });
  console.log(errorCounter)
  if (errorCounter == Object.keys(schedulesData).length) {
    alert("Ocorreu um erro e por isso não foram adicionados novos critérios por favor corriga a formula!")
  }
  return schedulesData

}


/**
 * Extrai os nomes das colunas da expressão que correspondem aos nomes das colunas fornecidos.
 * @param {string} expression - A expressão a ser avaliada.
 * @param {string[]} allColumnNames - Todos os nomes das colunas disponíveis para a extração.
 * @returns {string[]} - Os nomes das colunas encontradas na expressão.
 */
function extractColumnNamesFromExpression(expression, allColumnNames) {
  const foundColumnNames = [];

  allColumnNames.forEach(columnName => {
    if (expression.includes(columnName)) {
      foundColumnNames.push(columnName);
    }
  });

  return foundColumnNames;
}


/**
 * Substitui os nomes das colunas na expressão pelos valores correspondentes nas linhas de dados.
 * @param {string} expression - A expressão a ser avaliada.
 * @param {Object} row - A linha de dados contendo os valores das colunas.
 * @param {string[]} columnNames - Os nomes das colunas a serem substituídos.
 * @returns {string} - A expressão modificada com os valores das colunas substituídos.
 */
function substituteColumnNamesWithValues(expression, row, columnNames) {
  let modifiedExpression = expression;

  columnNames.forEach(columnName => {
    const value = row[columnName];
    modifiedExpression = modifiedExpression.replace(new RegExp(columnName, 'g'), `"${value}"`);
  });
  console.log(modifiedExpression)
  return modifiedExpression;
}


/**
 * Verifica se há correspondência exata de palavra na expressão.
 * @param {string} expression - A expressão a ser avaliada.
 * @param {string} input - A palavra a ser procurada na expressão.
 * @returns {boolean} - True se houver correspondência exata de palavra, caso contrário, False.
 */
function checkForExactWordMatch(expression, input) {
  const regexString = `\\b${input}\\b(?![\\w-])`;
  const regex = new RegExp(regexString);
  return regex.test(expression);
}


/**
 * Avalia um critério de texto dinâmico nos dados fornecidos e atualiza os resultados com os resultados da avaliação.
 * @param {Object} schedulesData - Os dados dos horários a serem avaliados.
 * @param {string} column - O nome da coluna que contém os dados de texto a serem avaliados.
 * @param {string} inputText - O texto de entrada a ser comparado com os dados de texto da coluna.
 * @returns {Object} - Os resultados atualizados com os resultados da avaliação do critério de texto dinâmico.
 */
function evaluateDynamicTextCriterium(schedulesData, column, inputText) {
  const inputParsed = inputText.split('.').join(' ') //Problema com o Tabulator 
  const fieldName = `${column}=${inputParsed}`;
  Object.keys(schedulesData).forEach((scheduleId) => {
    let counter = 0;
    const schedule = schedulesData[scheduleId];

    schedule.data.forEach((row, index) => {
      //if (math.compareText(row[column], inputText) === 0) {
      if (checkForExactWordMatch(row[column], inputText)) {
        schedule.data[index][fieldName] = true
        counter++;
      } else {
        schedule.data[index][fieldName] = false
      }
    });
    console.log(`Dynamic criterium (${fieldName}): ${counter}`);
    schedule.criteriums[fieldName] = counter;
  });
  return schedulesData;
}


/**
 * Atualiza o dropdown dos critérios dinâmicos com os valores dos cabeçalhos fornecidos.
 * @param {HTMLElement} dropdown - O elemento dropdown a ser atualizado.
 */
function updateDynamicCriteriums(dropdown) {
  dropdown.innerHTML = '';
  //console.log("Teste " + dictionary)
  for (let value of Object.values(dictionary)) {
    const option = document.createElement('option');
    option.value = value;
    option.text = value;
    dropdown.appendChild(option);
  }
}


/**
 * Cria um dicionário com as características de cada sala a partir dos dados fornecidos.
 * @param {Object} results - Os resultados dos dados do ficheiro das salas.
 * @returns {Object} - Um dicionário contendo as características de cada sala.
 */
function createClassRoomsDictionary(results) {
  const classroomDictionary = {};

  results.data.forEach(row => {
    const roomName = row['Nome sala'];
    const xMarkedHeaders = [];

    Object.keys(row).forEach(key => {
      if (row[key] === 'X' && key !== 'Edifício' && key !== 'Nome sala' && key !== 'Capacidade Normal' && key !== 'Capacidade Exame' && key !== 'Nº características') {
        xMarkedHeaders.push(key);
      }
    });

    if (roomName && xMarkedHeaders.length > 0) {
      classroomDictionary[roomName] = xMarkedHeaders;
    }
  });
  classRoomDictionary = classroomDictionary
}


/**
 * Ordena os dados dos horários alfabeticamente por nome de horário.
 * @param {Object} schedulesData - Os dados dos horários a serem ordenados.
 * @returns {Object} - Os dados dos horários ordenados por nome de horário.
 */
function orderSchedulesData(schedulesData) {
  const scheduleNames = Object.keys(schedulesData);
  scheduleNames.sort();
  let sortedSchedulesData = {};
  scheduleNames.forEach((scheduleName) => {
    sortedSchedulesData[scheduleName] = schedulesData[scheduleName];
  });
  return sortedSchedulesData
}


/**
 * Arredonda um tempo para a hora mais próxima.
 * @param {string} time - O tempo no formato 'HH:MM:SS' a ser arredondado.
 * @returns {string} - O tempo arredondado para a hora mais próxima no formato 'HH:MM:SS'.
 */
function roundToNearestHour(time) {
  const date = new Date(`2023-01-01T${time}`);
  date.setMinutes(0);
  date.setSeconds(0);
  date.setMilliseconds(0);
  return date.toTimeString().slice(0, 8);
}


/**
 * Cria uma tabela Tabulator modificável com os dados fornecidos.
 * @param {Object[]} scheduleData - Os dados a serem exibidos na tabela.
 * @param {HTMLElement[]} elementList - Uma lista de elementos HTML, onde o terceiro elemento será exibido.
 */
function createModifiableTabulator(scheduleData, elementList) {
  elementList[3].style.display = "block"
  const dictionaryValues = Object.values(dictionary); // Assuming 'dictionary' is your dictionary object

  const columns = Object.keys(scheduleData[0]).map(key => {
    let column = {
      title: key,
      field: key,
      editor: "input",
      headerFilter: "input",
    };

    // Check if 'key' is not present in the values of the 'dictionary'
    if (!dictionaryValues.includes(key)) {
      column.formatter = "tickCross";
      column.editor = ""
      column.headerFilter = ""
    }

    return column;
  });
  modifiableTable = new Tabulator("#modifiable-tabulator", {
    data: scheduleData,
    //layout: "fitData",
    autoColumns: false,
    width: "80%",
    columns: [
      ...columns,
    ],
    pagination: "local",
    paginationSize: 7,
  });
}


/**
 * Cria uma tabela Tabulator com os dados fornecidos.
 * @param {Object} schedulesData - Os dados dos horários a serem exibidos na tabela.
 * @param {HTMLElement} heatmapContainer - O contêiner onde será exibido o gráfico de heatmap.
 * @param {HTMLElement} downloadContainer - O contêiner onde será inserido o botão de download.
 * @param {HTMLElement} modifiableTabulator - O elemento onde será inserida a tabela Tabulator modificável.
 * @param {HTMLElement[]} elementList - Uma lista de elementos HTML.
 * @param {HTMLElement[]} graphs - Uma lista de elementos HTML que representam gráficos.
 */
function createTabulator(schedulesData, heatmapContainer, downloadContainer, modifiableTabulator, elementList, graphs) {
  console.log(schedulesData)
  const scheduleIds = Object.keys(schedulesData);

  const firstSchedule = schedulesData[scheduleIds[0]];
  const criteria = Object.keys(firstSchedule.criteriums);

  const columns = [
    { formatter: "rowSelection", title: "Selecionado", headerSort: false },
    { title: "Horários", field: "scheduleId" },
    ...criteria.map((criterion) => ({
      title: criterion,
      field: criterion,
    })),
  ];

  const tableData = scheduleIds.map((id) => {
    const rowData = { scheduleId: id };
    criteria.forEach((criterion) => {
      rowData[criterion] = schedulesData[id].criteriums[criterion] || "-";
    });
    return rowData;
  });

  table = new Tabulator("#chart-container", {
    data: tableData,
    columns: columns,
    layout: "fitColumns",
    selectable: 1,
  });

  table.on("rowSelectionChanged", function (data, rows, selected, deselected) { //TODO Terminar
    if (data.length !== 0) {
      let selectedScheduleData = schedulesData[data[0]['scheduleId']].data
      console.log(selectedScheduleData)
      createHeatMap(selectedScheduleData, elementList, '')
      elementList[5].style.display = "block"
      createTop10Chart(selectedScheduleData)
      createPieChart(selectedScheduleData)
      createRequisitesChart(selectedScheduleData)
      modifiableDataTabulator = createModifiableTabulator(selectedScheduleData, elementList)
      insertDownloadButton(downloadContainer, selectedScheduleData, elementList);
    }
    else {
      heatmapContainer.innerHTML = ""
      downloadContainer.innerHTML = ""
      modifiableTabulator.innerHTML = ""
      heatmapFilter.innerHTML = ""
      graphs.forEach(graph => {
        graph.innerHTML = '';
      });
      if (modifiableTabulator.classList.contains('tabulator')) {
        modifiableTabulator.classList.remove('tabulator');
        for (let i = 2; i < h4Elements.length; i++) {
          h4Elements[i].style.display = 'none';
        }
      }
    }
  });
}


/**
 * Adiciona um valor à lista global se o valor ainda não estiver presente e não for uma string vazia.
 * @param {string} inputValue - O valor a ser adicionado à lista global.
 * @param {Array} list - A lista global onde o valor será adicionado.
 */
function addToGlobalList(inputValue, list) {
  if (!list.includes(inputValue) && inputValue !== "") {
    //list.push(inputValue);
    list.unshift(inputValue);
  }
}


/**
 * Preenche um elemento de lista suspensa com as opções fornecidas.
 * @param {string} elementID - O ID do elemento HTML onde as opções serão preenchidas.
 * @param {Array} list - A lista de valores que serão usados como opções.
 */
function populateOptions(elementID, list) {
  const datalist = document.getElementById(elementID);
  datalist.innerHTML = ""; // Clear existing options

  list.forEach(item => {
    const option = document.createElement("option");
    option.value = item;
    datalist.appendChild(option);
  });
}


/**
 * Insere botões de download no contêiner especificado para baixar os dados selecionados.
 * @param {HTMLElement} downloadContainer - O contêiner onde os botões de download serão inseridos.
 * @param {Object[]} selectedScheduleData - Os dados do horário selecionado para download.
 * @param {HTMLElement[]} elementList - Uma lista de elementos HTML.
 */
function insertDownloadButton(downloadContainer, selectedScheduleData, elementList) {
  elementList[4].style.display = "block"
  const buttonJSON = document.createElement('button');
  buttonJSON.textContent = 'Download JSON';
  buttonJSON.onclick = function () {
    downloadFile(selectedScheduleData, false);
  };
  downloadContainer.appendChild(buttonJSON);
  const buttonCSV = document.createElement('button');
  buttonCSV.textContent = 'Download CSV';
  buttonCSV.onclick = function () {
    downloadFile(selectedScheduleData, true);
  };
  downloadContainer.appendChild(buttonCSV);
}


/**
 * Faz o download dos dados selecionados em um formato específico (CSV ou JSON).
 * @param {Object[]} selectedScheduleData - Os dados do horário selecionado para download.
 * @param {boolean} csv - Indica se o download será em formato CSV (true) ou JSON (false).
 */
function downloadFile(selectedScheduleData, csv) {
  console.log(modifiableTable.getData()) //TODO Usar estes dados para criar os ficheiros 
  let fileData, blob, filename, filteredData;
  const link = document.createElement('a');

  if (csv === true) {
    const dictionaryValues = Object.values(dictionary);
    const headers = Object.keys(selectedScheduleData[0]).filter(key => dictionaryValues.includes(key));
    const dataRows = selectedScheduleData.map(row => {
      return headers.map(header => row[header]).join(csvSeparator);
    });

    fileData = [headers.join(csvSeparator), ...dataRows].join('\n');
    blob = new Blob([new Uint8Array([0xEF, 0xBB, 0xBF]), fileData], { type: 'text/csv;charset=utf-8' });
    filename = 'data.csv';
  } else {
    filteredData = selectedScheduleData.map(row => {
      const filteredRow = {};
      Object.keys(row).forEach(key => {
        if (dictionary[key]) {
          filteredRow[dictionary[key]] = row[key];
        }
      });
      return filteredRow;
    });

    fileData = JSON.stringify(filteredData, null, 2);
    blob = new Blob([new Uint8Array([0xEF, 0xBB, 0xBF]), fileData], { type: 'application/json;charset=utf-8' });

    filename = 'data.json';
  }

  link.href = URL.createObjectURL(blob);
  link.download = filename;
  document.body.appendChild(link);
  link.click();

  // Remove the link from the body
  document.body.removeChild(link);
}


/**
 * Cria e exibe um gráfico de linha com a contagem de critérios dos horários.
 * @param {HTMLElement[]} elementList - Uma lista de elementos HTML relacionados ao gráfico de linha.
 */
function createLineChart(elementList) {
  elementList[0].style.display = "block";
  elementList[1].style.display = "block";
  const scheduleIds = Object.keys(schedulesData);
  const criteria = Object.keys(schedulesData[scheduleIds[0]].criteriums);
  const lineChartData = {
    chart: {
      caption: "Contagem de Critérios dos Horários",
      xAxisName: "Critérios",
      yAxisName: "Nº de Ocurrências",
      theme: "fusion",
    },
    categories: [
      {
        category: criteria.map((criterion) => ({ label: criterion })),
      },
    ],
    dataset: scheduleIds.map((id) => ({
      seriesname: id,
      data: criteria.map((criterion) => ({
        value: schedulesData[id].criteriums[criterion] || 0,
      })),
    })),
  };

  new FusionCharts({
    type: "msline",
    renderAt: "line-chart-container",
    height: "400",
    width: "100%",
    dataFormat: "json",
    dataSource: lineChartData,
  }).render();
}


/**
 * Conta o uso das salas com base no horário de início das aulas.
 * @param {Object[]} scheduleData - Os dados do horário das aulas.
 * @returns {Object} - Um objeto contendo o número de vezes que cada sala foi usada em cada horário de início arredondado para a hora mais próxima.
 */
function countRoomUsageByStartTime(scheduleData) {
  const roomUsageByStartTime = {};
  scheduleData.forEach(row => {
    const startTime = row[dictionary['Início']]
    const roomName = row[dictionary['Sala da aula']];
    if (startTime && roomName) {
      const roundedStartTime = roundToNearestHour(startTime);
      const key = `${roomName}/${roundedStartTime}`;
      roomUsageByStartTime[key] = (roomUsageByStartTime[key] || 0) + 1;
    }
  });

  return roomUsageByStartTime;
}


/**
 * Manipula a mudança no valor do menu suspenso do dia da semana e atualiza os dados exibidos conforme necessário.
 * @param {Object[]} selectedScheduleData - Os dados do horário selecionado.
 * @param {HTMLElement[]} elementList - Uma lista de elementos HTML relacionados à interface.
 * @param {boolean} isFirst - Indica se é a primeira chamada da função.
 * @returns {Object[]} - Os dados filtrados com base no dia da semana selecionado.
 */
function handleDropdownChange(selectedScheduleData, elementList, isFirst) {
  const selectedDayOfWeek = document.getElementById('dayOfWeekDropdown').value;
  console.log("Aconteceu")
  // Filter data based on the selected day of week
  const filteredData = (selectedDayOfWeek === 'all') ?
    selectedScheduleData :
    selectedScheduleData.filter(item => item[dictionary['Dia da Semana']] === selectedDayOfWeek);
  if (isFirst) {
    return filteredData
  } else {
    createHeatMap(selectedScheduleData, elementList, filteredData)
  }
}


/**
 * Encontra a primeira e última data dos dados filtrados.
 * @param {Object[]} filteredData - Os dados filtrados.
 * @returns {Object | null} - Um objeto contendo a primeira e última data dos dados filtrados ou null se os dados estiverem vazios.
 */
function findFirstAndLastDate(filteredData) {
  if (filteredData.length === 0) {
    return null;
  }

  const diaValues = filteredData.map(item => parseDate(item[dictionary['Dia']]));

  diaValues.sort((a, b) => a - b);
  console.log(diaValues)
  const firstDate = formatDate(diaValues[0]);
  const lastDate = formatDate(diaValues[diaValues.length - 1]);
  console.log(firstDate, lastDate)
  return { firstDate, lastDate };
}


/**
 * Analisa uma string de data no formato "dd/mm/yyyy" e retorna um objeto Date correspondente.
 * @param {string} dateString - A string de data no formato "dd/mm/yyyy".
 * @returns {Date} - O objeto Date correspondente à data analisada.
 */
function parseDate(dateString) {
  const [day, month, year] = dateString.split('/').map(Number);
  return new Date(year, month - 1, day); // Month is zero-based in JavaScript Dates
}


/**
 * Formata um objeto Date como uma string no formato "dd/mm/yyyy".
 * @param {Date} date - O objeto Date a ser formatado.
 * @returns {string} - A data formatada como uma string no formato "dd/mm/yyyy".
 */
function formatDate(date) {
  const day = date.getDate().toString().padStart(2, '0');
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
}


/**
 * Cria um mapa de calor com base nos dados do cronograma selecionado e os exibe no elemento especificado.
 * @param {Object[]} selectedScheduleData - Os dados do cronograma selecionado.
 * @param {HTMLElement[]} elementList - Uma lista de elementos HTML relacionados à exibição do mapa de calor.
 * @param {Object[]} filteredData - Os dados do cronograma filtrados para exibição no mapa de calor.
 */
function createHeatMap(selectedScheduleData, elementList, filteredData) {
  if (filteredData === '') {
    const dropdownContainer = document.getElementById('heatmap-filter');
    dropdownContainer.innerHTML = `
      <label for="dayOfWeekDropdown">Selecionar Dia da Semana:</label>
      <select id="dayOfWeekDropdown">
        ${getDayOfWeekOptions(selectedScheduleData)}
      </select>
      <br>
      <h4 id="h4-date"></h4>
    `;
    document.getElementById('dayOfWeekDropdown').addEventListener('change', () => handleDropdownChange(selectedScheduleData, elementList, false));
    filteredData = handleDropdownChange(selectedScheduleData, elementList, true)
  }
  dates = findFirstAndLastDate(filteredData)
  document.getElementById('h4-date').textContent = "Os dados apresentados abaixo representam o intervalo de dias entre " + dates.firstDate + " e " + dates.lastDate + "."
  document.getElementById('h4-date').style.display = "block"
  elementList[2].style.display = "block"
  const roomUsageByStartTime = countRoomUsageByStartTime(filteredData)
  console.log(roomUsageByStartTime)
  // Converta os dados para o formato esperado pela FusionCharts
  const heatMapChartData = [];
  for (var key in roomUsageByStartTime) {
    var roomName = key.split('/')[0];
    var startTime = key.split('/')[1];
    heatMapChartData.push({
      "rowid": startTime,
      "columnid": roomName,
      "value": `${roomUsageByStartTime[key]}`
    });
  }
  heatMapChartData.sort((a, b) => {
    const timeA = a.rowid;
    const timeB = b.rowid;
    return timeA.localeCompare(timeB);
  });
  console.log(JSON.stringify(heatMapChartData))

  const values = heatMapChartData.map(item => parseInt(item.value, 10));


  function getDayOfWeekOptions(data) {
    const uniqueDaysOfWeek = [...new Set(data.map(item => item[dictionary['Dia da Semana']]))];
    return uniqueDaysOfWeek.map(dayOfWeek => `<option value="${dayOfWeek}">${dayOfWeek}</option>`).join('');
  }

  // document.getElementById('dayOfWeekDropdown').addEventListener('change', handleDropdownChange(selectedScheduleData));
  // Step 2: Find the maximum and minimum values
  const maxValue = Math.max(...values);
  const minValue = Math.min(...values);

  // Step 3: Calculate the interval
  const interval = (maxValue - minValue) / 4;

  // Step 4: Define variables for starting values of each category
  const categoryStart1 = minValue;
  const categoryStart2 = minValue + interval;
  const categoryStart3 = minValue + 2 * interval;
  const categoryStart4 = minValue + 3 * interval;

  console.log(categoryStart1, categoryStart2, categoryStart3, minValue, maxValue)

  // Configurações do gráfico
  const heatMapConfig = {
    type: 'heatmap',
    renderAt: 'heatmap-container',
    width: '100%',
    height: '800',
    dataFormat: 'json',
    dataSource: {
      "chart": {
        caption: 'Contagem de ocupação de salas',
        subcaption: 'Por hora de início e dia da semana',
        theme: 'fusion',
      },
      "dataset": [
        {
          "data": heatMapChartData
        }
      ],
      "colorrange": {
        "gradient": "1",
        "startlabel": "Muito Livre",
        "code": "00A000",
        "color": [
          {
            "code": "00C000",
            "minvalue": `${categoryStart1}`,
            "maxvalue": `${categoryStart2}`,
            "label": "Livre"
          },
          {
            "code": "B0B000",
            "minvalue": `${categoryStart2}`,
            "maxvalue": `${categoryStart3}`,
            "label": "Média Ocupação"
          },
          {
            "code": "FFA040",
            "minvalue": `${categoryStart3}`,
            "maxvalue": `${categoryStart4}`,
            "label": "Ocupado"
          },
          {
            "code": "A02020",
            "minvalue": `${categoryStart4}`,
            "maxvalue": `${maxValue}`,
            "label": "Muito Ocupado"
          }
        ]
      }
    }
  };

  console.log("Length of heatMapChartData:", heatMapChartData.length);

  // Render FusionCharts
  FusionCharts.ready(function () {
    try {
      new FusionCharts(heatMapConfig).render();
    } catch (error) {
      console.error("Erro ao renderizar mapa de calor:", error);
    }
  });

}


/**
 * Cria um gráfico de barras representando as 10 salas com mais sobrelotações.
 * @param {Object[]} data - Os dados do cronograma contendo informações sobre as salas e sobrelotações.
 */
function createTop10Chart(data) {
  const overcrowdingMap = new Map();
  console.log(data)
  // Loop through the data and count OverCrowding occurrences for each Sala
  data.forEach(entry => {
    const sala = entry[dictionary['Sala da aula']];
    const overcrowding = entry['Sobrelotações'];
    //console.log(sala, overcrowding)
    if (overcrowding && sala) {
      if (!overcrowdingMap.has(sala)) {
        overcrowdingMap.set(sala, 1);
      } else {
        const currentCount = overcrowdingMap.get(sala);
        overcrowdingMap.set(sala, currentCount + 1);
      }
    }
  });
  console.log(overcrowdingMap)
  // Sort the map by value in descending order
  const sortedMap = new Map([...overcrowdingMap.entries()].sort((a, b) => b[1] - a[1]));

  // Extract top 10 Salas with most Overcrowding
  const top10 = Array.from(sortedMap.entries()).slice(0, 10);

  // Prepare data for FusionCharts
  const chartData = top10.map(([sala, count]) => ({
    label: sala,
    value: count,
  }));

  // FusionCharts configuration object
  const chartConfig = {
    type: 'bar2d',
    renderAt: 'extra-graph1', // Provide the div id where you want to render the chart
    width: '100%',
    height: '600',
    dataFormat: 'json',
    dataSource: {
      chart: {
        paletteColors: '#0066ff',
        caption: 'Top 10 Salas com mais Sobrelotações',
        xAxisName: 'Salas',
        yAxisName: 'Número de Sobrelotações',
        rotateLabels: '1',
        theme: 'fusion',
      },
      data: chartData,
    },
  };

  // Render FusionCharts
  FusionCharts.ready(function () {
    const fusionChart = new FusionCharts(chartConfig);
    fusionChart.render();
  });
}


/**
 * Cria um gráfico de pizza que analisa a atribuição de salas com base nos critérios 'Requisitos não cumpridos' e 'Aulas Sem Sala'.
 * @param {Object[]} data - Os dados do cronograma contendo informações sobre a atribuição de salas.
 */
function createPieChart(data) {
  let dataLength = data.length
  const criteriaMap = new Map([
    ['Atribuição Incorreta', 0],
    ['Sala por atribuir', 0],
    ['Atribuição Correta', 0]
  ]);

  data.forEach(entry => {
    const requisitesNotMet = entry['Requisitos não cumpridos'];
    const noClassroom = entry['Aulas Sem Sala'];

    if (requisitesNotMet === true && noClassroom === false) {
      criteriaMap.set('Atribuição Incorreta', criteriaMap.get('Atribuição Incorreta') + 1);
    } else if (noClassroom === true) {
      criteriaMap.set('Sala por atribuir', criteriaMap.get('Sala por atribuir') + 1);
    } else if (requisitesNotMet === false && noClassroom === false) {
      criteriaMap.set('Atribuição Correta', criteriaMap.get('Atribuição Correta') + 1);
    }
  });

  // Prepare data for FusionCharts
  const chartData = [];
  criteriaMap.forEach((value, key) => {
    chartData.push({ label: key, value });
  });

  // FusionCharts configuration object
  const chartConfig = {
    type: 'pie2d',
    renderAt: 'extra-graph2', // Replace with your container ID
    width: '100%',
    height: '600',
    dataFormat: 'json',
    dataSource: {
      chart: {
        paletteColors: '#7fc7d9, #0f1035, #0066ff',
        caption: 'Análise de Atribuição de Salas',
        plottooltext: "<b>$percentValue</b> das salas têm uma $label",
        subCaption: 'Total de Ocorrências: ' + dataLength,
        showPercentValues: '0',
        showLabels: '0',
        alignCaptionWithCanvas: '0',
        captionPadding: '0',
        decimals: '1',
        theme: 'fusion',
        legendposition: "bottom",
        showlegend: "1",
      },
      data: chartData // This is the data prepared earlier
    }
  };

  // Render FusionCharts
  FusionCharts.ready(function () {
    const fusionChart = new FusionCharts(chartConfig);
    fusionChart.render();
  });
}


/**
 * Cria um gráfico de rosca que analisa as características da sala que não correspondem aos requisitos.
 * @param {Object[]} data - Os dados do cronograma contendo informações sobre as características da sala e se os requisitos foram cumpridos.
 */
function createRequisitesChart(data) {

  const newMap = new Map();

  // Iterate through each key-value pair in the map
  let counter = 0
  data.forEach(entry => {
    const requisitesNotMet = entry['Requisitos não cumpridos'];
    const characteristics = entry[dictionary['Características da sala pedida para a aula']];
    if (characteristics && requisitesNotMet) {
      counter++
      if (!newMap.has(characteristics)) {
        newMap.set(characteristics, 1);
      } else {
        const currentCount = newMap.get(characteristics) + 1;
        newMap.set(characteristics, currentCount);
      }
    }
  })

  console.log("New Map:", newMap);


  const labels = Array.from(newMap.keys());
  const counts = Array.from(newMap.values());

  // FusionCharts configuration
  const chartConfig = {
    type: 'doughnut2d',
    width: '100%',
    height: '600',
    dataFormat: 'json',
    renderAt: 'extra-graph3',
    dataSource: {
      chart: {
        plottooltext: "<b>$percentValue</b> das caraterísticas não pedidas são <b>$label</b>",
        caption: 'Análise das caraterísticas não correspondidas',
        subcaption: 'Total de Ocorrências: ' + counter,
        showPercentValues: '0',
        showLabels: '0',
        showLegend: '1',
        legendposition: "bottom",
        theme: 'fusion'
      },
      data: labels.map((label, index) => ({
        label: label,
        value: counts[index]
      }))
    }
  };


  // Render the FusionCharts instance
  FusionCharts.ready(function () {
    new FusionCharts(chartConfig).render();
  });

}




