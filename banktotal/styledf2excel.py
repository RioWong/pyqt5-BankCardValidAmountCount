from StyleFrame import StyleFrame, Styler, utils


def style_df(df):
    # Create StyleFrame object that wrap our DataFrame and assign default style.
    defaults = {'font': utils.fonts.aharoni, 'font_size': 11}
    sf = StyleFrame(df, styler_obj=Styler(**defaults))

    # Style the headers of the table
    header_style = Styler(bold=True, font_size=11)
    sf.apply_headers_style(styler_obj=header_style)

    # Change the columns width and the rows height
    sf.set_column_width(columns=sf.columns, width=20)
    sf.set_row_height(rows=sf.row_indexes, height=25)

    return sf


def style_df_all(df):
    # Create StyleFrame object that wrap our DataFrame and assign default style.
    defaults = {'font': utils.fonts.aharoni, 'font_size': 10}
    sf = StyleFrame(df, styler_obj=Styler(**defaults))

    # Style the headers of the table
    header_style = Styler(bold=True, font_size=11)
    sf.apply_headers_style(styler_obj=header_style)

    # Change the columns width and the rows height
    sf.set_column_width(columns=sf.columns, width=12)
    sf.set_column_width(columns=['transDate', 'description', 'remark', 'amountMoney'], width=20)
    sf.set_column_width(columns=["shoppingsheetId", "billId", "relationId"], width=30)
    sf.set_row_height(rows=sf.row_indexes, height=25)
    # Set the background color to red where the test marked as 'failed'
    valid_style = Styler(bg_color=utils.colors.red, font_color=utils.colors.white, **defaults)
    invalid_style = Styler(bg_color=utils.colors.green, font_color=utils.colors.black, **defaults)
    # sf.apply_style_by_indexes(indexes_to_style=sf[sf['是否有效流水'] == 0],
    #                           cols_to_style='amountMoney',
    #                           styler_obj=valid_style)
    sf.apply_style_by_indexes(indexes_to_style=sf[sf['是否有效流水'] == 1],
                              cols_to_style='amountMoney',
                              styler_obj=invalid_style)
    # 单元格左对齐
    col_style = Styler(horizontal_alignment=utils.horizontal_alignments.left, font_size=10)
    # sf.set_column_width(columns=["remark"], width=80)
    # sf.apply_column_style(cols_to_style=["remark", 'description', 'nameOnOppositeCard'],
    #                       styler_obj=col_style)
    return sf


def styledf2excel(outfile_path, df_all, df_pivot, df_client_info, df_ave):
    print(outfile_path)
    ew = StyleFrame.ExcelWriter(outfile_path)
    sf_all = style_df_all(df_all)
    # sf_all = datetime_style_df(sf_all)
    sf_pivot = style_df(df_pivot)
    sf_client = style_df(df_client_info)
    sf_ave = style_df(df_ave)
    sf_all.to_excel(ew, sheet_name="原始流水标记",
                    columns_and_rows_to_freeze='A2',
                    row_to_add_filters=0, )
    sf_pivot.to_excel(ew, sheet_name="各月份有效流水统计", index=False)
    sf_ave.to_excel(ew, sheet_name="日均存款余额", index=False)
    sf_client.to_excel(ew, sheet_name="客户信息", index=False)
    ew.save()

