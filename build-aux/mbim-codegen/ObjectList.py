# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*-
#
# SPDX-License-Identifier: LGPL-2.1-or-later
#
# Copyright (C) 2013 - 2018 Aleksander Morgado <aleksander@aleksander.es>
#

import string

from Message import Message
from Struct import Struct
import utils

"""
Check field to see if it holds a struct
"""
def set_struct_usage(struct, fields):
    for field in fields:
        if field['format'] == 'struct' and field['struct-type'] == struct.name:
            struct.single_member = True
            break
        if field['format'] == 'ms-struct' and field['struct-type'] == struct.name:
            struct.single_member = True
            struct.ms_struct = True
            break
        if field['format'] == 'ref-struct-array' and field['struct-type'] == struct.name:
            struct.ref_struct_array_member = True
            break
        if field['format'] == 'struct-array' and field['struct-type'] == struct.name:
            struct.struct_array_member = True
            break
        if field['format'] == 'ms-struct-array' and field['struct-type'] == struct.name:
            struct.ms_struct_array_member = True
            break


"""
The ObjectList class handles the generation of all commands and types for a given
specific service
"""
class ObjectList:

    """
    Constructor
    """
    def __init__(self, objects_dictionary):
        self.command_list = []
        self.struct_list = []
        self.service_list = []

        # Loop items in the list, creating Message objects for the messages
        service_iter = ''
        mbimex_service_iter = ''
        mbimex_version_iter = ''

        for object_dictionary in objects_dictionary:
            if object_dictionary['type'] == 'Command':
                if service_iter == '':
                    raise ValueError('Service name not specified before the first command')
                self.command_list.append(Message(service_iter, mbimex_service_iter, mbimex_version_iter, object_dictionary))
            elif object_dictionary['type'] == 'Struct':
                self.struct_list.append(Struct(service_iter, mbimex_service_iter, mbimex_version_iter, object_dictionary))
            elif object_dictionary['type'] == 'Service':
                service_iter = object_dictionary['name']
                self.service_list.append(service_iter)
                if 'mbimex-service' in object_dictionary:
                    mbimex_service_iter = object_dictionary['mbimex-service']
                    mbimex_version_iter = object_dictionary['mbimex-version']
                else:
                    mbimex_service_iter = ''
                    mbimex_version_iter = ''
            else:
                raise ValueError('Cannot handle object type \'%s\'' % object_dictionary['type'])

        if not self.service_list:
            raise ValueError('Service name not specified')

        # Populate struct usages
        for struct in self.struct_list:
            for command in self.command_list:
                set_struct_usage(struct, command.query)
                set_struct_usage(struct, command.set)
                set_struct_usage(struct, command.response)
                set_struct_usage(struct, command.notification)

    """
    Emit the structs and commands handling implementation
    """
    def emit(self, hfile, cfile):
        # Emit all structs
        for item in self.struct_list:
            item.emit(hfile, cfile)
        # Emit all commands
        for item in self.command_list:
            item.emit(hfile, cfile)


    """
    Emit support for printing messages in a single service
    """
    def emit_printable_service(self, hfile, cfile, service):
        translations = { 'service_underscore' : utils.build_underscore_name(service),
                         'service'            : service }

        template = (
            '\n'
            'G_GNUC_INTERNAL\n'
            'gchar *\n'
            '__mbim_message_${service_underscore}_get_printable_fields (\n'
            '    const MbimMessage *message,\n'
            '    const gchar *line_prefix,\n'
            '    GError **error);\n')
        hfile.write(string.Template(template).substitute(translations))

        template = (
            '\n'
            'static const GetPrintableCallbacks ${service_underscore}_get_printable_callbacks[] = {\n')

        for item in self.command_list:
            if item.service == service:
                translations['message'] = utils.build_underscore_name (item.fullname)
                translations['cid']     = item.cid_enum_name
                inner_template = (
                    '    [${cid}] = {\n')
                if item.has_query:
                    inner_template += (
                        '        .query_cb = ${message}_query_get_printable,\n')
                if item.has_set:
                    inner_template += (
                        '        .set_cb = ${message}_set_get_printable,\n')
                if item.has_response:
                    inner_template += (
                        '        .response_cb = ${message}_response_get_printable,\n')
                if item.has_notification:
                    inner_template += (
                        '        .notification_cb = ${message}_notification_get_printable,\n')
                inner_template += (
                    '    },\n')
                template += (string.Template(inner_template).substitute(translations))

        template += (
            '};\n'
            '\n'
            'gchar *\n'
            '__mbim_message_${service_underscore}_get_printable_fields (\n'
            '    const MbimMessage *message,\n'
            '    const gchar *line_prefix,\n'
            '    GError **error)\n'
            '{\n'
            '    guint32 cid;\n'
            '\n'
            '    switch (mbim_message_get_message_type (message)) {\n'
            '        case MBIM_MESSAGE_TYPE_COMMAND: {\n'
            '            cid = mbim_message_command_get_cid (message);\n'
            '            if (cid < G_N_ELEMENTS (${service_underscore}_get_printable_callbacks)) {\n'
            '                switch (mbim_message_command_get_command_type (message)) {\n'
            '                    case MBIM_MESSAGE_COMMAND_TYPE_QUERY:\n'
            '                        if (${service_underscore}_get_printable_callbacks[cid].query_cb)\n'
            '                            return ${service_underscore}_get_printable_callbacks[cid].query_cb (message, line_prefix, error);\n'
            '                        break;\n'
            '                    case MBIM_MESSAGE_COMMAND_TYPE_SET:\n'
            '                        if (${service_underscore}_get_printable_callbacks[cid].set_cb)\n'
            '                            return ${service_underscore}_get_printable_callbacks[cid].set_cb (message, line_prefix, error);\n'
            '                        break;\n'
            '                    case MBIM_MESSAGE_COMMAND_TYPE_UNKNOWN:\n'
            '                    default:\n'
            '                        g_set_error (error,\n'
            '                                     MBIM_CORE_ERROR,\n'
            '                                     MBIM_CORE_ERROR_INVALID_MESSAGE,\n'
            '                                     \"Invalid command type\");\n'
            '                        return NULL;\n'
            '                }\n'
            '            }\n'
            '            break;\n'
            '        }\n'
            '\n'
            '        case MBIM_MESSAGE_TYPE_COMMAND_DONE:\n'
            '            cid = mbim_message_command_done_get_cid (message);\n'
            '            if (cid < G_N_ELEMENTS (${service_underscore}_get_printable_callbacks)) {\n'
            '                if (${service_underscore}_get_printable_callbacks[cid].response_cb)\n'
            '                    return ${service_underscore}_get_printable_callbacks[cid].response_cb (message, line_prefix, error);\n'
            '            }\n'
            '            break;\n'
            '\n'
            '        case MBIM_MESSAGE_TYPE_INDICATE_STATUS:\n'
            '            cid = mbim_message_indicate_status_get_cid (message);\n'
            '            if (cid < G_N_ELEMENTS (${service_underscore}_get_printable_callbacks)) {\n'
            '                if (${service_underscore}_get_printable_callbacks[cid].notification_cb)\n'
            '                    return ${service_underscore}_get_printable_callbacks[cid].notification_cb (message, line_prefix, error);\n'
            '            }\n'
            '            break;\n'
            '\n'
            '        case MBIM_MESSAGE_TYPE_OPEN: \n'
            '        case MBIM_MESSAGE_TYPE_CLOSE: \n'
            '        case MBIM_MESSAGE_TYPE_INVALID: \n'
            '        case MBIM_MESSAGE_TYPE_HOST_ERROR: \n'
            '        case MBIM_MESSAGE_TYPE_OPEN_DONE: \n'
            '        case MBIM_MESSAGE_TYPE_CLOSE_DONE: \n'
            '        case MBIM_MESSAGE_TYPE_FUNCTION_ERROR: \n'
            '        default:\n'
            '            g_set_error (error,\n'
            '                         MBIM_CORE_ERROR,\n'
            '                         MBIM_CORE_ERROR_INVALID_MESSAGE,\n'
            '                         \"No contents expected in this message type\");\n'
            '            return NULL;\n'
            '    }\n'
            '\n'
            '    g_set_error (error,\n'
            '                 MBIM_CORE_ERROR,\n'
            '                 MBIM_CORE_ERROR_UNSUPPORTED,\n'
            '                 \"Unsupported message\");\n'
            '    return NULL;\n'
            '}\n')

        cfile.write(string.Template(template).substitute(translations))

    def emit_printable(self, hfile, cfile):

        template = (
            '\n'
            '/*****************************************************************************/\n'
            '/* Service helpers for printable fields */\n'
            '\n'
            '#if defined (LIBMBIM_GLIB_COMPILATION)\n')
        hfile.write(template)

        template = (
            '\n'
            'typedef struct {\n'
            '  gchar * (* query_cb)        (const MbimMessage *message, const gchar *line_prefix, GError **error);\n'
            '  gchar * (* set_cb)          (const MbimMessage *message, const gchar *line_prefix, GError **error);\n'
            '  gchar * (* response_cb)     (const MbimMessage *message, const gchar *line_prefix, GError **error);\n'
            '  gchar * (* notification_cb) (const MbimMessage *message, const gchar *line_prefix, GError **error);\n'
            '} GetPrintableCallbacks;\n')
        cfile.write(template)

        for service in self.service_list:
            self.emit_printable_service(hfile, cfile, service)

        template = (
            '\n'
            '#endif\n')
        hfile.write(template)


    """
    Emit the section for a single service
    """
    def emit_sections_service(self, sfile, service):
        translations = { 'service_dashed' : utils.build_dashed_name(service),
                         'service'        : service }

        # Emit section header
        template = (
            '\n'
            '<SECTION>\n'
            '<FILE>mbim-${service_dashed}</FILE>\n'
            '<TITLE>${service}</TITLE>\n')
        sfile.write(string.Template(template).substitute(translations))

        # Emit subsection per type
        for struct in self.struct_list:
            if struct.service == service:
                struct.emit_section_content(sfile)

        # Emit subsection per command
        for command in self.command_list:
            if command.service == service:
                command.emit_section_content(sfile)

        sfile.write(
            '</SECTION>\n')

    def emit_sections(self, sfile):
        for service in self.service_list:
            self.emit_sections_service(sfile, service)
