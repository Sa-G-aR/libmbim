/* -*- Mode: C; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
/* SPDX-License-Identifier: GPL-2.0-or-later */
/*
 * Copyright (C) 2013 - 2014 Aleksander Morgado <aleksander@aleksander.es>
 */

#include <config.h>

#include "mbim-uuid.h"

static void
compare_uuid_strings (const MbimUuid *uuid,
                      const gchar *other_uuid_str)
{
    gchar *uuid_str;

    uuid_str = mbim_uuid_get_printable (uuid);
    g_assert_cmpstr (uuid_str, ==, other_uuid_str);
    g_free (uuid_str);
}

static void
test_uuid_basic_connect (void)
{
    compare_uuid_strings (MBIM_UUID_BASIC_CONNECT,
                          "a289cc33-bcbb-8b4f-b6b0-133ec2aae6df");
}

static void
test_uuid_sms (void)
{
    compare_uuid_strings (MBIM_UUID_SMS,
                          "533fbeeb-14fe-4467-9f90-33a223e56c3f");
}

static void
test_uuid_ussd (void)
{
    compare_uuid_strings (MBIM_UUID_USSD,
                          "e550a0c8-5e82-479e-82f7-10abf4c3351f");
}

static void
test_uuid_phonebook (void)
{
    compare_uuid_strings (MBIM_UUID_PHONEBOOK,
                          "4bf38476-1e6a-41db-b1d8-bed289c25bdb");
}

static void
test_uuid_stk (void)
{
    compare_uuid_strings (MBIM_UUID_STK,
                          "d8f20131-fcb5-4e17-8602-d6ed3816164c");
}

static void
test_uuid_auth (void)
{
    compare_uuid_strings (MBIM_UUID_AUTH,
                          "1d2b5ff7-0aa1-48b2-aa52-50f15767174e");
}

static void
test_uuid_dss (void)
{
    compare_uuid_strings (MBIM_UUID_DSS,
                          "c08a26dd-7718-4382-8482-6e0d583c4d0e");
}

static void
test_uuid_ms_firmware_id (void)
{
    compare_uuid_strings (MBIM_UUID_MS_FIRMWARE_ID,
                          "e9f7dea2-feaf-4009-93ce-90a3694103b6");
}

static void
test_uuid_ms_host_shutdown (void)
{
    compare_uuid_strings (MBIM_UUID_MS_HOST_SHUTDOWN,
                          "883b7c26-985f-43fa-9804-27d7fb80959c");
}

static void
test_uuid_ms_sar (void)
{
    compare_uuid_strings (MBIM_UUID_MS_SAR,
                          "68223d04-9f6c-4e0f-822d-28441fb72340");
}

static void
test_uuid_intel_firmware_update (void)
{
    compare_uuid_strings (MBIM_UUID_INTEL_FIRMWARE_UPDATE,
                          "0ed374cb-f835-4474-bc11-3b3fd76f5641");
}

static void
test_uuid_ms_basic_connect_extensions (void)
{
    compare_uuid_strings (MBIM_UUID_MS_BASIC_CONNECT_EXTENSIONS,
                          "3d01dcc5-fef5-4d05-0d3a-bef7058e9aaf");
}

static void
test_uuid_quectel (void)
{
    compare_uuid_strings (MBIM_UUID_QUECTEL,
                          "11223344-5566-7788-99aa-bbccddeeff11");
}

/*****************************************************************************/

static void
compare_uuid_types (const gchar *uuid_str,
                    const MbimUuid *other_uuid)
{
    MbimUuid uuid;

    g_assert (mbim_uuid_from_printable (uuid_str, &uuid));
    g_assert (mbim_uuid_cmp (&uuid, other_uuid));
}

static void
invalid_uuid_str (const gchar *uuid_str)
{
    MbimUuid uuid;

    g_assert (mbim_uuid_from_printable (uuid_str, &uuid) == FALSE);
}

static void
test_uuid_valid (void)
{
    compare_uuid_types ("a289cc33-bcbb-8b4f-b6b0-133ec2aae6df",
                        MBIM_UUID_BASIC_CONNECT);
}

static void
test_uuid_valid_camelcase (void)
{
    compare_uuid_types ("A289cC33-BcBb-8B4f-B6b0-133Ec2Aae6Df",
                        MBIM_UUID_BASIC_CONNECT);
}

static void
test_uuid_invalid_empty (void)
{
    invalid_uuid_str ("");
}

static void
test_uuid_invalid_short (void)
{
    invalid_uuid_str ("a289cc33-bcbb-8b4f-b6b0-");
}

static void
test_uuid_invalid_long (void)
{
    invalid_uuid_str ("a289cc33-bcbb-8b4f-b6b0-133ec2aae6dfaaa");
}

static void
test_uuid_invalid_dashes (void)
{
    /* Dashes one too early */
    invalid_uuid_str ("289cc33-bcbb-8b4f-b6b0-133ec2aae6dfa");
}

static void
test_uuid_invalid_no_hex (void)
{
    invalid_uuid_str ("hello wo-rld -8b4f-b6b0-133ec2aae6df");
}

/*****************************************************************************/

static void
test_uuid_custom (void)
{
    static const gchar *nick = "register_custom";
    static const MbimUuid uuid_custom = {
        .a = { 0x52, 0x65, 0x67, 0x69 },
        .b = { 0x73, 0x74 },
        .c = { 0x65, 0x72 },
        .d = { 0x20, 0x63 },
        .e = { 0x75, 0x73, 0x74, 0x6f, 0x6d, 0x21 }
    };
    guint service;

    /* SERVICE_AUTH is not a custom service */
    g_assert (!mbim_service_id_is_custom (MBIM_SERVICE_AUTH));

    service = mbim_register_custom_service (&uuid_custom, nick);
    g_assert (mbim_service_id_is_custom (service));
    g_assert (g_strcmp0 (mbim_service_lookup_name (service), nick) == 0);
    g_assert (mbim_uuid_cmp (mbim_uuid_from_service (service), &uuid_custom));
    g_assert (mbim_uuid_to_service (&uuid_custom) == service);
    g_assert (mbim_unregister_custom_service (service));

    /* once removed service is not custom */
    g_assert (!mbim_service_id_is_custom (service));
}

/*****************************************************************************/

int main (int argc, char **argv)
{
    g_test_init (&argc, &argv, NULL);

    g_test_add_func ("/libmbim-glib/uuid/basic-connect",               test_uuid_basic_connect);
    g_test_add_func ("/libmbim-glib/uuid/sms",                         test_uuid_sms);
    g_test_add_func ("/libmbim-glib/uuid/ussd",                        test_uuid_ussd);
    g_test_add_func ("/libmbim-glib/uuid/phonebook",                   test_uuid_phonebook);
    g_test_add_func ("/libmbim-glib/uuid/stk",                         test_uuid_stk);
    g_test_add_func ("/libmbim-glib/uuid/auth",                        test_uuid_auth);
    g_test_add_func ("/libmbim-glib/uuid/dss",                         test_uuid_dss);
    g_test_add_func ("/libmbim-glib/uuid/ms-firmware-id",              test_uuid_ms_firmware_id);
    g_test_add_func ("/libmbim-glib/uuid/ms-host-shutdown",            test_uuid_ms_host_shutdown);
    g_test_add_func ("/libmbim-glib/uuid/ms-sar",                      test_uuid_ms_sar);
    g_test_add_func ("/libmbim-glib/uuid/intel-firmware-update",       test_uuid_intel_firmware_update);
    g_test_add_func ("/libmbim-glib/uuid/ms-basic-connect-extensions", test_uuid_ms_basic_connect_extensions);
    g_test_add_func ("/libmbim-glib/uuid/quectel",                     test_uuid_quectel);

    g_test_add_func ("/libmbim-glib/uuid/valid",           test_uuid_valid);
    g_test_add_func ("/libmbim-glib/uuid/valid/camelcase", test_uuid_valid_camelcase);

    g_test_add_func ("/libmbim-glib/uuid/invalid/empty",  test_uuid_invalid_empty);
    g_test_add_func ("/libmbim-glib/uuid/invalid/short",  test_uuid_invalid_short);
    g_test_add_func ("/libmbim-glib/uuid/invalid/long",   test_uuid_invalid_long);
    g_test_add_func ("/libmbim-glib/uuid/invalid/dashes", test_uuid_invalid_dashes);
    g_test_add_func ("/libmbim-glib/uuid/invalid/no-hex", test_uuid_invalid_no_hex);

    g_test_add_func ("/libmbim-glib/uuid/custom", test_uuid_custom);

    return g_test_run ();
}
